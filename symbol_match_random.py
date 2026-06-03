import pygame
import random
import csv
import time
from datetime import datetime
from pathlib import Path

pygame.init()

BASE_W, BASE_H = 1024, 1024
WIDTH, HEIGHT = BASE_W, BASE_H

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Symbol Match Task")
clock = pygame.time.Clock()

BG=(0,0,140); CYAN=(0,255,255); GREEN=(0,255,0)
YELLOW=(255,255,0); WHITE=(245,245,245); RED=(255,0,0)

def fonts(scale):
    return (
        pygame.font.SysFont("timesnewroman", max(18, int(74*scale))),
        pygame.font.SysFont("timesnewroman", max(16, int(68*scale))),
        pygame.font.SysFont("arial", max(12, int(28*scale)), bold=True),
        pygame.font.SysFont("arial", max(12, int(32*scale)), bold=True),
    )

SYMBOLS=["╣","Ω","◀","δ","√","≡","¥","↕","æ"]

CSV_FILE="symbol_match_data.csv"
if not Path(CSV_FILE).exists():
    with open(CSV_FILE,"w",newline="",encoding="utf-8") as f:
        csv.writer(f).writerow(["trial","timestamp","symbol","display_number","is_match","response","correct","rt_ms"])

trial=0; correct_count=0; incorrect_count=0; last_rt=None; flash_until=0

def create_trial():
    syms=SYMBOLS[:]
    random.shuffle(syms)
    mapping={i+1:syms[i] for i in range(9)}
    truth=random.choice([True,False])
    number=random.randint(1,9)
    symbol=mapping[number] if truth else random.choice([s for s in syms if s!=mapping[number]])
    return mapping,symbol,number,truth

def draw_mapping(mapping, scale, symbol_font, number_font):
    margin=int(40*scale)
    gap=max(8,int(36*scale))
    box_w=(WIDTH-2*margin-gap*8)//9
    box_h=int(250*scale)
    top_h=box_h//2
    y=int(125*scale)
    for i in range(9):
        x=margin+i*(box_w+gap)
        pygame.draw.rect(screen,CYAN,(x,y,box_w,box_h),max(1,int(4*scale)))
        pygame.draw.line(screen,CYAN,(x,y+top_h),(x+box_w,y+top_h),max(1,int(4*scale)))
        s=symbol_font.render(mapping[i+1],True,YELLOW)
        screen.blit(s,s.get_rect(center=(x+box_w//2,y+top_h//2)))
        n=number_font.render(str(i+1),True,WHITE)
        screen.blit(n,n.get_rect(center=(x+box_w//2,y+top_h+top_h//2)))

def draw_target(symbol, number, scale, symbol_font, number_font):
    w=int(120*scale); h=int(255*scale)
    x=WIDTH//2-w//2; y=int(455*scale)
    pygame.draw.rect(screen,GREEN,(x,y,w,h),max(1,int(5*scale)))
    pygame.draw.line(screen,GREEN,(x,y+h//2),(x+w,y+h//2),max(1,int(5*scale)))
    s=symbol_font.render(symbol,True,YELLOW)
    screen.blit(s,s.get_rect(center=(x+w//2,y+h//4)))
    n=number_font.render(str(number),True,WHITE)
    screen.blit(n,n.get_rect(center=(x+w//2,y+3*h//4)))

def draw_ui(scale, info_font, bottom_font):
    t=info_font.render("RIGHT CLICK = Match (True) | LEFT CLICK = Non-Match (False)",True,WHITE)
    screen.blit(t,t.get_rect(center=(WIDTH//2,int(820*scale))))
    d=info_font.render("Decide as quickly and accurately as possible.",True,YELLOW)
    screen.blit(d,d.get_rect(center=(WIDTH//2,int(900*scale))))

    bar_y=HEIGHT-int(95*scale)
    pygame.draw.line(screen,WHITE,(0,bar_y),(WIDTH,bar_y),2)
    sec=WIDTH/5
    for i in range(1,5):
        pygame.draw.line(screen,WHITE,(int(sec*i),bar_y),(int(sec*i),HEIGHT),2)

    acc=0 if trial==0 else round(correct_count/max(1,trial)*100,1)
    items=[(f"Trial: {trial}",WHITE),(f"Correct: {correct_count}",GREEN),
           (f"Incorrect: {incorrect_count}",RED),(f"Accuracy: {acc}%",WHITE),
           (f"RT: {'--' if last_rt is None else int(last_rt)} ms",WHITE)]
    for i,(txt,col) in enumerate(items):
        surf=bottom_font.render(txt,True,col)
        screen.blit(surf,surf.get_rect(center=(sec*i+sec/2,HEIGHT-int(48*scale))))

mapping,target_symbol,target_number,truth=create_trial()
trial_start=time.perf_counter()

running=True
while running:
    scale=min(WIDTH/BASE_W, HEIGHT/BASE_H)
    symbol_font, number_font, info_font, bottom_font = fonts(scale)

    clock.tick(60)
    screen.fill(RED if pygame.time.get_ticks()<flash_until else BG)

    draw_mapping(mapping, scale, symbol_font, number_font)
    draw_target(target_symbol,target_number, scale, symbol_font, number_font)
    draw_ui(scale, info_font, bottom_font)
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running=False

        elif event.type==pygame.KEYDOWN:
            if event.key == pygame.K_LEFTBRACKET:
                WIDTH=max(700, int(WIDTH*0.9))
                HEIGHT=max(700, int(HEIGHT*0.9))
                screen=pygame.display.set_mode((WIDTH,HEIGHT), pygame.RESIZABLE)
            elif event.key == pygame.K_RIGHTBRACKET:
                WIDTH=min(2200, int(WIDTH*1.1))
                HEIGHT=min(2200, int(HEIGHT*1.1))
                screen=pygame.display.set_mode((WIDTH,HEIGHT), pygame.RESIZABLE)

        elif event.type==pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.w, event.h
            screen=pygame.display.set_mode((WIDTH,HEIGHT), pygame.RESIZABLE)

        elif event.type==pygame.MOUSEBUTTONDOWN and event.button in (1,3):
            rt=(time.perf_counter()-trial_start)*1000
            response_truth=(event.button==3)
            correct=(response_truth==truth)

            if correct: globals()['correct_count']+=1
            else:
                globals()['incorrect_count']+=1
                flash_until=pygame.time.get_ticks()+250

            globals()['trial']+=1
            globals()['last_rt']=rt

            with open(CSV_FILE,"a",newline="",encoding="utf-8") as f:
                csv.writer(f).writerow([trial,datetime.now().isoformat(),
                target_symbol,target_number,truth,
                "TRUE" if response_truth else "FALSE",correct,round(rt,2)])

            mapping,target_symbol,target_number,truth=create_trial()
            trial_start=time.perf_counter()

pygame.quit()
