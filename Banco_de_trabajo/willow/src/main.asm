; =====================================================================
;  WILLOW'S FLATULENT ADVENTURE  -  Sega Master System
;  (c) 2026 Tony C. Ware
;  main.asm - vectors, boot, core helpers
; =====================================================================
 include "defs.inc"

 org $0000
 di
 im 1
 ld sp,$DFF0
 jp boot

 org $0038
irq_handler:
 push af
 in a,(VDP_CTRL)             ; ack frame interrupt
 ld a,1
 ld (vblank_flag),a
 push bc
 push de
 push hl
 push ix
 call snd_update
 pop ix
 pop hl
 pop de
 pop bc
 ld hl,frame_cnt
 inc (hl)
 pop af
 ei
 reti

 org $0066
nmi_handler:                  ; PAUSE button
 push af
 ld a,(game_state)
 cp GS_GAME
 jr nz,.np
 ld a,(paused)
 xor 1
 ld (paused),a
.np:
 pop af
 retn

; ---------------------------------------------------------------------
boot:
 ; Sega mapper: banks 0,1,2 -> linear 48KB
 xor a
 ld ($FFFC),a
 ld ($FFFD),a
 inc a
 ld ($FFFE),a
 inc a
 ld ($FFFF),a
 ; clear RAM $C000-$DFEF
 ld hl,$C000
 ld de,$C001
 ld bc,$1FEE
 ld (hl),0
 ldir
 ld sp,$DFF0
 call snd_init
 call vdp_init
 call vram_clear
 ; load sprite tiles & palette, common BG tiles
 ld hl,VRAM_SPR
 call vdp_waddr
 ld hl,spr_tiles
 ld de,SPR_NTILES*32
 call vram_copy
 ld hl,0
 call vdp_waddr
 ld hl,bg_common_tiles
 ld de,BG_COMMON_TILES*32
 call vram_copy
 ld hl,sprite_palette
 ld a,16
 call load_palette16
 ld hl,$2A3B
 ld (rnd_seed),hl
 ; default hiscore 5000
 ld a,$50
 ld (hiscore+1),a
 ei
 jp title_screen

; ---------------------------------------------------------------------
; VDP helpers
; ---------------------------------------------------------------------
vdp_init:
 ld hl,vdp_regs
 ld b,11
 ld c,$80
.l:
 ld a,(hl)
 out (VDP_CTRL),a
 ld a,c
 out (VDP_CTRL),a
 inc hl
 inc c
 djnz .l
 ret
vdp_regs:
 db $06,$A0,$FF,$FF,$FF,$FF,$FF,$00,$00,$00,$FF

; a = value, b = register
vdp_reg:
 out (VDP_CTRL),a
 ld a,b
 or $80
 out (VDP_CTRL),a
 ret

display_on:
 ld a,$E0
 ld b,1
 jr vdp_reg
display_off:
 ld a,$A0
 ld b,1
 jr vdp_reg

; hl = vram address (write)
vdp_waddr:
 ld a,l
 out (VDP_CTRL),a
 ld a,h
 or $40
 out (VDP_CTRL),a
 ret

; hl = src, de = length
vram_copy:
.l:
 ld a,(hl)
 out (VDP_DATA),a
 inc hl
 dec de
 ld a,d
 or e
 jr nz,.l
 ret

vram_clear:
 ld hl,0
 call vdp_waddr
 ld de,$4000
.l:
 xor a
 out (VDP_DATA),a
 dec de
 ld a,d
 or e
 jr nz,.l
 ret

; hl = 16 colour palette, a = first cram index (0 or 16)
load_palette16:
 out (VDP_CTRL),a
 ld a,$C0
 out (VDP_CTRL),a
 ld b,16
.l:
 ld a,(hl)
 out (VDP_DATA),a
 inc hl
 djnz .l
 ret

; black palette (fade helper)
palette_black:
 xor a
 out (VDP_CTRL),a
 ld a,$C0
 out (VDP_CTRL),a
 ld b,16
 xor a
.l:
 out (VDP_DATA),a
 djnz .l
 ret

; b = row, c = col -> hl = name table vram address
name_addr:
 ld l,b
 ld h,0
 add hl,hl
 add hl,hl
 add hl,hl
 add hl,hl
 add hl,hl
 ld a,c
 add a,l
 ld l,a
 add hl,hl
 ld de,VRAM_NAME
 add hl,de
 ret

; print zero-terminated string at row b col c (direct to VRAM)
; hl = string
print_at:
 push hl
 call name_addr
 call vdp_waddr
 pop hl
print_cont:
.l:
 ld a,(hl)
 or a
 ret z
 push hl
 ld e,a
 ld d,0
 ld hl,font_map
 add hl,de
 ld a,(hl)
 out (VDP_DATA),a
 xor a
 out (VDP_DATA),a
 pop hl
 inc hl
 jr .l

; clear row b (direct)
clear_row:
 ld c,0
 call name_addr
 call vdp_waddr
 ld b,64
 xor a
.l:
 out (VDP_DATA),a
 djnz .l
 ret

; print BCD byte a as two digits (VRAM pointer already set)
print_bcd:
 push af
 rrca
 rrca
 rrca
 rrca
 and 15
 inc a              ; font: ' '=0, '0'=1
 out (VDP_DATA),a
 xor a
 out (VDP_DATA),a
 pop af
 and 15
 inc a
 out (VDP_DATA),a
 xor a
 out (VDP_DATA),a
 ret

; ---------------------------------------------------------------------
; frame sync / input / random
; ---------------------------------------------------------------------
wait_vblank:
 xor a
 ld (vblank_flag),a
.w:
 halt
 ld a,(vblank_flag)
 or a
 jr z,.w
 ret

; wait a frames
wait_frames:
 push af
 call wait_vblank
 pop af
 dec a
 jr nz,wait_frames
 ret

read_pad:
 in a,(PAD_PORT)
 cpl
 and $3F
 ld b,a
 ld a,(pad_now)
 ld (pad_old),a
 cpl
 and b
 ld (pad_new),a
 ld a,b
 ld (pad_now),a
 ret

; returns a = random byte (xorshift16)
rand:
 push hl
 ld hl,(rnd_seed)
 ld a,h
 rra
 ld a,l
 rra
 xor h
 ld h,a
 ld a,l
 rra
 ld a,h
 rra
 xor l
 ld l,a
 xor h
 ld h,a
 ld (rnd_seed),hl
 pop hl
 ret

; wait until no button held, then until button 1/2 or timeout (a frames, 0=forever)
; returns nz if button pressed
wait_button:
 ld (tmp3),a
.rel:
 call wait_vblank
 call read_pad
 ld a,(pad_now)
 and $30
 jr nz,.rel
.w:
 call wait_vblank
 call read_pad
 ld a,(pad_new)
 and $30
 ret nz
 ld a,(tmp3)
 or a
 jr z,.w
 dec a
 ld (tmp3),a
 jr nz,.w
 xor a
 ret

 include "title.asm"
 include "game.asm"
 include "player.asm"
 include "enemy.asm"
 include "objects.asm"
 include "sprites.asm"
 include "hud.asm"
 include "sound.asm"

code_end:

; =====================================================================
;  DATA
; =====================================================================
spr_tiles:
 incbin "../build/spr.bin"
bg_common_tiles:
 incbin "../build/bgcommon.bin"
sprite_palette:
 incbin "../build/spal.bin"
font_map:
 incbin "../build/fontmap.bin"
portrait_tiles:
 incbin "../build/portrait.bin"
portrait_map:
 incbin "../build/portrait.map"
portrait_pal:
 incbin "../build/portrait.pal"
room_tiles:
 incbin "../build/room0.bin"
 incbin "../build/room1.bin"
 incbin "../build/room2.bin"
 incbin "../build/room3.bin"
room_pals:
 incbin "../build/room0.pal"
 incbin "../build/room1.pal"
 incbin "../build/room2.pal"
 incbin "../build/room3.pal"
 include "../build/levels.inc"
 include "../build/sound.inc"
 include "../build/gfx.inc"
data_end:
 assert data_end <= $7FF0, "ROM too big for 32KB"
