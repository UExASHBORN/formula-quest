import pygame
import sys
from questions import QuestionBank
from progress import ProgressTracker
from ui import Button, TextInputBox, draw_wrapped_text

class Game:
    def __init__(self):
        pygame.init()
        self.width = 1000
        self.height = 700
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Formula Quest — Math & CS Memory Trainer")
        
        self.clock = pygame.time.Clock()
        
        self.bg_color = (15, 23, 42)
        self.card_bg = (30, 41, 59)
        self.text_main = (248, 250, 252)
        self.text_muted = (148, 163, 184)
        self.accent_green = (34, 197, 94)
        self.accent_red = (239, 68, 68)
        self.accent_blue = (59, 130, 246)
    
        self.font_title = pygame.font.SysFont("Arial", 36, bold=True)
        self.font_header = pygame.font.SysFont("Arial", 24, bold=True)
        self.font_body = pygame.font.SysFont("Arial", 18)
        self.font_small = pygame.font.SysFont("Arial", 14)
    
        self.qb = QuestionBank()
        self.tracker = ProgressTracker()
        
        self.state = "MENU"
        self.current_index = 0
        self.active_questions = []
        
        self.selected_option = None
        self.mcq_answered = False
        self.mcq_feedback = ""
    
        self.input_box = TextInputBox(100, 380, 500, 45, self.font_body)
        self.hard_feedback = ""
        self.show_hint_flag = False
        self.revealed_flag = False
        self.is_revision = False
    
        self.init_menu_buttons()

    def init_menu_buttons(self):
        bw, bh, bx = 420, 50, 290
        start_y = 190
        gap = 14

        self.btn_easy = Button(bx, start_y, bw, bh, "1. Easy Mode (Learn & Browse)", self.font_header)
        self.btn_toc = Button(bx, start_y + (bh + gap), bw, bh, "2. Table of Contents (Topic Jump)", self.font_header, bg_color=(37, 99, 235), hover_color=(59, 130, 246))
        self.btn_medium = Button(bx, start_y + 2 * (bh + gap), bw, bh, "3. Medium Mode (Randomized)", self.font_header)
        self.btn_hard = Button(bx, start_y + 3 * (bh + gap), bw, bh, "4. Hard Mode (Recall)", self.font_header)
        self.btn_progress = Button(bx, start_y + 4 * (bh + gap), bw, bh, "5. Progress & Revision", self.font_header)
        self.btn_exit = Button(bx, start_y + 5 * (bh + gap), bw, bh, "6. Exit", self.font_header, bg_color=(127, 29, 29), hover_color=(185, 28, 28))

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(60)

    def handle_events(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if self.state == "MENU":
                if self.btn_easy.is_clicked(event):
                    self.start_easy_mode()
                elif self.btn_toc.is_clicked(event):
                    self.state = "TOC"
                    self.setup_toc_buttons()
                elif self.btn_medium.is_clicked(event):
                    self.start_medium_mode(revision=False)
                elif self.btn_hard.is_clicked(event):
                    self.start_hard_mode(revision=False)
                elif self.btn_progress.is_clicked(event):
                    self.state = "PROGRESS"
                elif self.btn_exit.is_clicked(event):
                    pygame.quit()
                    sys.exit()

            elif self.state == "TOC":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if hasattr(self, 'btn_menu') and self.btn_menu.is_clicked(event):
                        self.state = "MENU"
                    elif hasattr(self, 'toc_buttons'):
                        for topic, idx, btn in self.toc_buttons:
                            if btn.is_clicked(event):
                                self.active_questions = self.qb.get_all_formulas()
                                self.current_index = idx
                                self.state = "EASY"

            elif self.state == "EASY":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if hasattr(self, 'btn_prev') and self.btn_prev.is_clicked(event):
                        self.current_index = (self.current_index - 1) % len(self.active_questions)
                    elif hasattr(self, 'btn_next') and self.btn_next.is_clicked(event):
                        self.current_index = (self.current_index + 1) % len(self.active_questions)
                    elif hasattr(self, 'btn_menu') and self.btn_menu.is_clicked(event):
                        self.state = "MENU"

            elif self.state == "MEDIUM":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if hasattr(self, 'btn_menu') and self.btn_menu.is_clicked(event):
                        self.state = "MENU"
                    elif hasattr(self, 'btn_next') and self.btn_next.is_clicked(event):
                        self.next_medium_question()
                    elif not self.mcq_answered and hasattr(self, 'option_buttons'):
                        for idx, btn in enumerate(self.option_buttons):
                            if btn.is_clicked(event):
                                self.check_medium_answer(idx)

            elif self.state == "HARD":
                submitted = self.input_box.handle_event(event)
                if submitted:
                    self.check_hard_answer()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if hasattr(self, 'btn_menu') and self.btn_menu.is_clicked(event):
                        self.state = "MENU"
                    elif hasattr(self, 'btn_submit') and self.btn_submit.is_clicked(event):
                        self.check_hard_answer()
                    elif hasattr(self, 'btn_hint') and self.btn_hint.is_clicked(event):
                        self.show_hint_flag = True
                    elif hasattr(self, 'btn_reveal') and self.btn_reveal.is_clicked(event):
                        self.reveal_hard_answer()
                    elif hasattr(self, 'btn_next') and self.btn_next.is_clicked(event):
                        self.next_hard_question()

            elif self.state == "PROGRESS":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if hasattr(self, 'btn_menu') and self.btn_menu.is_clicked(event):
                        self.state = "MENU"
                    elif hasattr(self, 'btn_rev_practice') and self.btn_rev_practice.is_clicked(event):
                        self.start_medium_mode(revision=True)
                    elif hasattr(self, 'btn_rev_recall') and self.btn_rev_recall.is_clicked(event):
                        self.start_hard_mode(revision=True)

    def update(self):
        pass

    def setup_toc_buttons(self):
        topics = self.qb.get_topics()
        self.toc_buttons = []
        start_y = 150
        bx = 150
        bw, bh = 700, 38
        gap = 10
        
        for i, (topic, idx) in enumerate(topics.items()):
            btn = Button(bx, start_y + i * (bh + gap), bw, bh, f"Jump to: {topic} (Q #{idx + 1})", self.font_body, bg_color=(30, 41, 59), hover_color=(59, 130, 246))
            self.toc_buttons.append((topic, idx, btn))

    def start_easy_mode(self):
        self.active_questions = self.qb.get_all_formulas()
        self.current_index = 0
        self.state = "EASY"

    def start_medium_mode(self, revision=False):
        self.is_revision = revision
        if revision:
            inc_ids = self.tracker.get_incorrect_formulas()
            self.active_questions = [q for q in self.qb.get_all_formulas() if q["id"] in inc_ids]
        else:
            self.active_questions = self.qb.get_practice_questions()
            
        self.current_index = 0
        if not self.active_questions:
            self.state = "PROGRESS"
            return
        self.state = "MEDIUM"
        self.setup_medium_question()

    def setup_medium_question(self):
        self.mcq_answered = False
        self.selected_option = None
        self.mcq_feedback = ""
        q = self.active_questions[self.current_index]
        
        self.option_buttons = []
        start_y = 320
        bw, bh = 800, 45
        for i, option in enumerate(q["mcq_options"]):
            self.option_buttons.append(
                Button(100, start_y + i * 55, bw, bh, f"{chr(65+i)}. {option}", self.font_body, bg_color=(30, 41, 59), hover_color=(51, 65, 85))
            )

    def check_medium_answer(self, option_idx):
        if self.mcq_answered:
            return
        self.mcq_answered = True
        self.selected_option = option_idx
        q = self.active_questions[self.current_index]
        
        selected_text = q["mcq_options"][option_idx]
        is_correct = (selected_text == q["correct_answer"])
        
        self.tracker.record_attempt(q["id"], is_correct)
        if is_correct:
            self.mcq_feedback = "Correct! Well done."
        else:
            self.mcq_feedback = f"Incorrect. Correct answer: {q['correct_answer']}"

    def next_medium_question(self):
        self.current_index += 1
        if self.current_index >= len(self.active_questions):
            self.state = "MENU"
        else:
            self.setup_medium_question()

    def start_hard_mode(self, revision=False):
        self.is_revision = revision
        if revision:
            inc_ids = self.tracker.get_incorrect_formulas()
            self.active_questions = [q for q in self.qb.get_all_formulas() if q["id"] in inc_ids]
        else:
            self.active_questions = self.qb.get_recall_questions()
            
        self.current_index = 0
        if not self.active_questions:
            self.state = "PROGRESS"
            return
        self.state = "HARD"
        self.setup_hard_question()

    def setup_hard_question(self):
        self.input_box.clear()
        self.hard_feedback = ""
        self.show_hint_flag = False
        self.revealed_flag = False

    def check_hard_answer(self):
        if self.hard_feedback:
            return
        q = self.active_questions[self.current_index]
        user_ans = self.input_box.text.strip()
        
        if not user_ans:
            self.hard_feedback = "Please enter an answer before submitting."
            return

        normalized_user = user_ans.replace(" ", "").lower()
        accepted = [a.replace(" ", "").lower() for a in q["accepted_answers"]]
        accepted.append(q["correct_answer"].replace(" ", "").lower())

        is_correct = (normalized_user in accepted) and not self.revealed_flag
        
        if self.revealed_flag:
            self.tracker.record_attempt(q["id"], False)
            self.hard_feedback = f"Assisted (Revealed). Correct answer was: {q['correct_answer']}"
        elif is_correct:
            self.tracker.record_attempt(q["id"], True)
            self.hard_feedback = "Correct! Excellent recall."
        else:
            self.tracker.record_attempt(q["id"], False)
            self.hard_feedback = f"Incorrect. Correct answer: {q['correct_answer']}"

    def reveal_hard_answer(self):
        self.revealed_flag = True
        q = self.active_questions[self.current_index]
        self.input_box.text = q["correct_answer"]
        self.hard_feedback = "Answer revealed. (Marked as assisted/incorrect for revision)."

    def next_hard_question(self):
        self.current_index += 1
        if self.current_index >= len(self.active_questions):
            self.state = "MENU"
        else:
            self.setup_hard_question()

    def render(self):
        self.screen.fill(self.bg_color)

        if self.state == "MENU":
            self.render_menu()
        elif self.state == "TOC":
            self.render_toc()
        elif self.state == "EASY":
            self.render_easy()
        elif self.state == "MEDIUM":
            self.render_medium()
        elif self.state == "HARD":
            self.render_hard()
        elif self.state == "PROGRESS":
            self.render_progress()

        pygame.display.flip()

    def render_menu(self):
        title = self.font_title.render("FORMULA QUEST", True, self.text_main)
        subtitle = self.font_body.render("Master Mathematics & Computer Science Formulas for GATE, CAT & CMAT", True, self.text_muted)
        
        self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 50))
        self.screen.blit(subtitle, (self.width // 2 - subtitle.get_width() // 2, 95))

        self.btn_easy.draw(self.screen)
        self.btn_toc.draw(self.screen)
        self.btn_medium.draw(self.screen)
        self.btn_hard.draw(self.screen)
        self.btn_progress.draw(self.screen)
        self.btn_exit.draw(self.screen)

    def render_toc(self):
        h_surf = self.font_title.render("Table of Contents — Topic Jump", True, self.text_main)
        self.screen.blit(h_surf, (100, 30))

        sub_surf = self.font_body.render("Select a topic below to jump directly to that section:", True, self.text_muted)
        self.screen.blit(sub_surf, (100, 75))

        for topic, idx, btn in self.toc_buttons:
            btn.draw(self.screen)

        self.btn_menu = Button(750, 620, 150, 40, "Back to Menu", self.font_body, bg_color=(71, 85, 105), hover_color=(100, 116, 139))
        self.btn_menu.draw(self.screen)

    def render_easy(self):
        q = self.active_questions[self.current_index]
        
        header_text = f"Easy Mode (Learn) — [{self.current_index + 1} / {len(self.active_questions)}]"
        h_surf = self.font_header.render(header_text, True, self.text_main)
        self.screen.blit(h_surf, (100, 30))

        card_rect = pygame.Rect(100, 80, 800, 510)
        pygame.draw.rect(self.screen, self.card_bg, card_rect, border_radius=10)
        pygame.draw.rect(self.screen, (71, 85, 105), card_rect, 2, border_radius=10)

        topic_surf = self.font_small.render(f"Topic: {q['topic']} | Name: {q['name']}", True, self.accent_blue)
        self.screen.blit(topic_surf, (130, 105))

        notif_surf = self.font_header.render(q["notation"], True, self.text_main)
        self.screen.blit(notif_surf, (130, 145))

        expl_rect = pygame.Rect(130, 205, 740, 60)
        draw_wrapped_text(self.screen, f"Explanation: {q['explanation']}", self.font_body, self.text_muted, expl_rect)

        ex_rect = pygame.Rect(130, 285, 740, 60)
        draw_wrapped_text(self.screen, f"Example: {q['example_question']}", self.font_body, self.text_main, ex_rect)

        sol_rect = pygame.Rect(130, 365, 740, 180)
        sol_text = f"Answer: {q['correct_answer']}\nWorked Solution: {q['worked_solution']}"
        draw_wrapped_text(self.screen, sol_text, self.font_body, self.accent_green, sol_rect)

        self.btn_prev = Button(100, 615, 140, 40, "Previous", self.font_body)
        self.btn_next = Button(255, 615, 140, 40, "Next", self.font_body)
        self.btn_menu = Button(760, 615, 140, 40, "Back to Menu", self.font_body, bg_color=(71, 85, 105), hover_color=(100, 116, 139))

        self.btn_prev.draw(self.screen)
        self.btn_next.draw(self.screen)
        self.btn_menu.draw(self.screen)

    def render_medium(self):
        q = self.active_questions[self.current_index]
        mode_prefix = "Revision Practice" if self.is_revision else "Medium Mode (Randomized)"
        header_text = f"{mode_prefix} — [{self.current_index + 1} / {len(self.active_questions)}]"
        h_surf = self.font_header.render(header_text, True, self.text_main)
        self.screen.blit(h_surf, (100, 30))

        topic_surf = self.font_small.render(f"Topic: {q['topic']} | {q['name']}", True, self.accent_blue)
        self.screen.blit(topic_surf, (100, 70))

        q_rect = pygame.Rect(100, 100, 800, 80)
        draw_wrapped_text(self.screen, q['example_question'], self.font_header, self.text_main, q_rect)

        for idx, btn in enumerate(self.option_buttons):
            if self.mcq_answered:
                opt_text = q["mcq_options"][idx]
                if opt_text == q["correct_answer"]:
                    btn.bg_color = (20, 83, 45)
                elif idx == self.selected_option:
                    btn.bg_color = (127, 29, 29)
                else:
                    btn.bg_color = (30, 41, 59)
            btn.draw(self.screen)

        if self.mcq_answered:
            fb_color = self.accent_green if "Correct" in self.mcq_feedback else self.accent_red
            fb_surf = self.font_header.render(self.mcq_feedback, True, fb_color)
            self.screen.blit(fb_surf, (100, 540))

            sol_rect = pygame.Rect(100, 580, 600, 50)
            draw_wrapped_text(self.screen, f"Solution: {q['worked_solution']}", self.font_small, self.text_muted, sol_rect)

            self.btn_next = Button(750, 615, 150, 40, "Next Question", self.font_body)
            self.btn_next.draw(self.screen)

        self.btn_menu = Button(750, 25, 150, 35, "Back to Menu", self.font_body, bg_color=(71, 85, 105), hover_color=(100, 116, 139))
        self.btn_menu.draw(self.screen)

    def render_hard(self):
        q = self.active_questions[self.current_index]
        mode_prefix = "Revision Recall" if self.is_revision else "Hard Mode (Randomized Recall)"
        header_text = f"{mode_prefix} — [{self.current_index + 1} / {len(self.active_questions)}]"
        h_surf = self.font_header.render(header_text, True, self.text_main)
        self.screen.blit(h_surf, (100, 30))

        topic_surf = self.font_small.render(f"Topic: {q['topic']} | {q['name']}", True, self.accent_blue)
        self.screen.blit(topic_surf, (100, 70))

        q_rect = pygame.Rect(100, 110, 800, 80)
        draw_wrapped_text(self.screen, q['example_question'], self.font_header, self.text_main, q_rect)

        notation_hint_surf = self.font_small.render(f"Formula Reference / Notation: {q['notation']}", True, self.text_muted)
        self.screen.blit(notation_hint_surf, (100, 210))

        lbl = self.font_small.render("Type your exact answer below and press Enter or Submit:", True, self.text_main)
        self.screen.blit(lbl, (100, 340))
        self.input_box.draw(self.screen)

        self.btn_submit = Button(620, 370, 130, 45, "Submit", self.font_body, bg_color=(37, 99, 235), hover_color=(59, 130, 246))
        self.btn_hint = Button(100, 430, 140, 40, "Hint", self.font_body, bg_color=(71, 85, 105), hover_color=(100, 116, 139))
        self.btn_reveal = Button(260, 430, 160, 40, "Reveal Answer", self.font_body, bg_color=(127, 29, 29), hover_color=(185, 28, 28))

        self.btn_submit.draw(self.screen)
        self.btn_hint.draw(self.screen)
        self.btn_reveal.draw(self.screen)

        if self.show_hint_flag:
            hint_rect = pygame.Rect(100, 490, 800, 40)
            draw_wrapped_text(self.screen, f"Hint: {q['hint']}", self.font_small, self.accent_blue, hint_rect)

        if self.hard_feedback:
            fb_color = self.accent_green if "Correct" in self.hard_feedback else self.accent_red
            fb_surf = self.font_header.render(self.hard_feedback, True, fb_color)
            self.screen.blit(fb_surf, (100, 530))

            sol_rect = pygame.Rect(100, 570, 600, 60)
            draw_wrapped_text(self.screen, f"Solution: {q['worked_solution']}", self.font_small, self.text_muted, sol_rect)

            self.btn_next = Button(750, 615, 150, 40, "Next Question", self.font_body)
            self.btn_next.draw(self.screen)

        self.btn_menu = Button(750, 25, 150, 35, "Back to Menu", self.font_body, bg_color=(71, 85, 105), hover_color=(100, 116, 139))
        self.btn_menu.draw(self.screen)

    def render_progress(self):
        h_surf = self.font_title.render("Progress & Revision Dashboard", True, self.text_main)
        self.screen.blit(h_surf, (100, 40))

        stats = self.tracker.get_stats()
        
        card_rect = pygame.Rect(100, 110, 800, 280)
        pygame.draw.rect(self.screen, self.card_bg, card_rect, border_radius=10)
        pygame.draw.rect(self.screen, (71, 85, 105), card_rect, 2, border_radius=10)

        y_offset = 135
        lines = [
            f"Total Quiz Attempts: {stats['total_attempted']}",
            f"Correct Answers: {stats['correct_answers']}",
            f"Overall Accuracy: {stats['accuracy']:.2f}%",
            f"Formulas Needing Revision: {stats['incorrect_count']}"
        ]

        for line in lines:
            txt = self.font_header.render(line, True, self.text_main)
            self.screen.blit(txt, (130, y_offset))
            y_offset += 55

        self.btn_rev_practice = Button(100, 420, 280, 45, "Practice Incorrect (Medium)", self.font_body, bg_color=(37, 99, 235), hover_color=(59, 130, 246))
        self.btn_rev_recall = Button(400, 420, 280, 45, "Recall Incorrect (Hard)", self.font_body, bg_color=(37, 99, 235), hover_color=(185, 28, 28))
        self.btn_rev_practice.draw(self.screen)
        self.btn_rev_recall.draw(self.screen)

        if stats['incorrect_count'] == 0:
            no_inc = self.font_small.render("No incorrect formulas pending revision. Great job!", True, self.accent_green)
            self.screen.blit(no_inc, (100, 485))

        self.btn_menu = Button(750, 615, 150, 40, "Back to Menu", self.font_body, bg_color=(71, 85, 105), hover_color=(100, 116, 139))
        self.btn_menu.draw(self.screen)