import pygame

class Button:
    def __init__(self, x, y, width, height, text, font, bg_color=(45, 55, 72), hover_color=(66, 153, 225), text_color=(255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        current_bg = self.hover_color if self.rect.collidepoint(mouse_pos) else self.bg_color
        
        pygame.draw.rect(surface, current_bg, self.rect, border_radius=6)
        pygame.draw.rect(surface, (100, 116, 139), self.rect, 2, border_radius=6)
        
        # Safe string encoding replacement to prevent missing font glyph blocks (e.g. '×' -> 'x')
        safe_text = self.text.replace('×', 'x')
        text_surface = self.font.render(safe_text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

class TextInputBox:
    def __init__(self, x, y, width, height, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.text = ""
        self.active = False
        self.bg_color = (30, 41, 59)
        self.active_border_color = (66, 153, 225)
        self.inactive_border_color = (100, 116, 139)
        self.text_color = (255, 255, 255)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if len(event.unicode) > 0 and ord(event.unicode) >= 32:
                    self.text += event.unicode
        return False

    def draw(self, surface):
        border_color = self.active_border_color if self.active else self.inactive_border_color
        pygame.draw.rect(surface, self.bg_color, self.rect, border_radius=6)
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=6)
        
        safe_text = self.text.replace('×', 'x')
        text_surface = self.font.render(safe_text, True, self.text_color)
        surface.blit(text_surface, (self.rect.x + 12, self.rect.y + 10))

    def clear(self):
        self.text = ""

def draw_wrapped_text(surface, text, font, color, rect, line_spacing=6):
    safe_str_text = text.replace('×', 'x')
    words = safe_str_text.split(' ')
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        test_width, _ = font.size(test_line)
        if test_width <= rect.width:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    if current_line:
        lines.append(' '.join(current_line))
        
    y = rect.y
    for line in lines:
        if y + font.get_height() > rect.y + rect.height:
            break
        txt_surface = font.render(line, True, color)
        surface.blit(txt_surface, (rect.x, y))
        y += font.get_height() + line_spacing