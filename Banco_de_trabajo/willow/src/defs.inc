; =====================================================================
;  WILLOW'S FLATULENT ADVENTURE - Sega Master System
;  (c) 2026 Tony C. Ware
;  defs.inc - constants and RAM layout
; =====================================================================

; ---- ports ----
VDP_DATA    equ $BE
VDP_CTRL    equ $BF
PSG_PORT    equ $7F
PAD_PORT    equ $DC

; ---- pad bits (after cpl: 1 = pressed) ----
PAD_UP      equ 0
PAD_DOWN    equ 1
PAD_LEFT    equ 2
PAD_RIGHT   equ 3
PAD_B1      equ 4
PAD_B2      equ 5

; ---- VRAM ----
VRAM_NAME   equ $3800
VRAM_SAT    equ $3F00
VRAM_SPR    equ $2000

; ---- map / collision ----
COL_EMPTY   equ 0
COL_SOLID   equ 1
COL_PLAT    equ 2

; ---- entity struct (32 bytes, accessed with IX) ----
ENT_SIZE    equ 32
E_TYPE      equ 0
E_STATE     equ 1
E_XF        equ 2
E_X         equ 3
E_YF        equ 4
E_Y         equ 5
E_VXF       equ 6
E_VX        equ 7
E_VYF       equ 8
E_VY        equ 9
E_DIR       equ 10      ; 0 right, 1 left
E_TIMER     equ 11
E_ANIM      equ 12
E_TUFO      equ 13      ; gas level
E_TUFOT     equ 14      ; gas decay timer
E_FLAGS     equ 15      ; bit0 bald, bit1 onground, bit2 hitwall
E_BOUNCE    equ 16
E_COMBO     equ 17
E_AUX       equ 18
E_AUX2      equ 19
E_HP        equ 20
E_INV       equ 21
E_W         equ 22      ; width in pixels
E_H         equ 23      ; height

F_BALD      equ 0
F_GROUND    equ 1
F_WALL      equ 2

; entity types
T_NONE      equ 0
T_BOLA      equ 1
T_ESCOBA    equ 2
T_LAVADORA  equ 3
T_ASPIRA    equ 4

; enemy states
S_NORMAL    equ 0
S_BALL      equ 1
S_ROLL      equ 2
S_DYING     equ 3
S_APPEAR    equ 4

MAX_ENEMY   equ 8

; player states
P_PLAY      equ 0
P_DYING     equ 1
P_DANCE     equ 2

; puffs (8 bytes)
PUFF_SIZE   equ 8
PF_ACT      equ 0
PF_X        equ 1
PF_Y        equ 2
PF_DX       equ 3   ; signed px/frame
PF_DIST     equ 4
PF_BIG      equ 5
PF_ANIM     equ 6
MAX_PUFF    equ 3

; items (8 bytes)
ITEM_SIZE   equ 8
IT_TYPE     equ 0   ; 0 none, 1 atun, 2 pienso, 3 galleta, 4 sushi, 5 sardina, 6 leche
IT_X        equ 1
IT_Y        equ 2
IT_VY       equ 3
IT_TIMER    equ 4
IT_GROUND   equ 5
MAX_ITEM    equ 4

IT_ATUN     equ 1
IT_PIENSO   equ 2
IT_GALLETA  equ 3
IT_SUSHI    equ 4
IT_SARDINA  equ 5
IT_LECHE    equ 6

; particles (stars) 4 bytes
MAX_PART    equ 6
PART_SIZE   equ 4

; game states
GS_TITLE    equ 0
GS_GAME     equ 1

; ---- tuning ----
GRAVITY     equ $0030
MAXFALL     equ $04
JUMP_VEL    equ $FBC0       ; -4.25
TUFO_DECAY  equ 120         ; frames per gas level decay
ROLL_SPEED  equ 3

; ---- RAM ----
            rsset $C000
frame_cnt       rb 1
vblank_flag     rb 1
pad_now         rb 1
pad_old         rb 1
pad_new         rb 1        ; newly pressed
paused          rb 1
rnd_seed        rw 1
game_state      rb 1
difficulty      rb 1        ; 0 normal 1 hardcore
loop_num        rb 1        ; 0 first lap
room_num        rb 1        ; 0..3
screen_num      rb 1        ; 0..4
lives           rb 1
score           rb 3        ; BCD, little endian (score[0] = lowest 2 digits)
hiscore         rb 3
next_extend     rb 3        ; BCD
pw_atun         rb 1
pw_pienso       rb 1
pw_galleta      rb 1
enemies_left    rb 1
clear_timer     rb 1
hurry_timer     rw 1
hurry_state     rb 1        ; 0 none 1 warned 2 vacuum out
msg_timer       rb 1
hud_dirty       rb 1        ; bit0 score bit1 lives bit2 power bit3 msg bit4 bossbar bit5 hiscore
msg_ptr         rw 1
boss_active     rb 1
boss_hp         rb 1
boss_maxhp      rb 1
shake           rb 1
puff_cool       rb 1
fart_anim       rb 1
spr_count       rb 1        ; sprites used this frame
spr_rot         rb 1        ; flicker rotation
spawn_cool      rb 1
ready_timer     rb 1
combo_score     rb 1
tmp0            rb 1
tmp1            rb 1
tmp2            rb 1
tmp3            rb 1
enemy_speed     rb 1        ; speed bonus (0..)
willow_spd      rw 1
puff_range      rb 1
puff_power      rb 1
over_timer      rb 1
go_unused       rb 1
cur_level_ptr   rw 1
bolas_alive     rb 1

; sound driver
snd_mus_on      rb 1
snd_tempo       rb 1
snd_tick        rb 1
snd_sfx_ptr     rw 1
snd_cur_song    rb 1
snd_duck        rb 1
title_sel       rb 1
blink           rb 1
last_music      rb 1
boss_dead       rb 1
ending_flag     rb 1
pause_state     rb 1
next_action     rb 1
walk_anim       rb 1
kill_x          rb 1
kill_y          rb 1

            rsset $C200
colmap          rb 768      ; 32x24 collision map ($C200-$C4FF)

            rsset $C500
sat_y           rb 64
sat_xn          rb 128

            rsset $C600
player          rb ENT_SIZE
enemies         rb ENT_SIZE*MAX_ENEMY   ; $C620..$C71F
puffs           rb PUFF_SIZE*MAX_PUFF
items           rb ITEM_SIZE*MAX_ITEM
parts           rb PART_SIZE*MAX_PART
hud_buf         rb 64

            rsset $C800
snd_ch          rb 64       ; 4 channels x 16 bytes
            rsset $D000
namebuf         rb 1536     ; 32x24 name table build buffer
ram_end         rb 1
