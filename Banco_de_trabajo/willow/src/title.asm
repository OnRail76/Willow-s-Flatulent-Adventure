; =====================================================================
;  title.asm - title screen with Willow's portrait
; =====================================================================
title_screen:
 di
 call display_off
 call snd_stop_music
 ld a,GS_TITLE
 ld (game_state),a
 xor a
 ld (paused),a
 call clear_name_table
 call hide_sprites
 ; portrait tiles -> tile 96
 ld hl,ROOM_TILE_BASE*32
 call vdp_waddr
 ld hl,portrait_tiles
 ld de,PORTRAIT_TILES*32
 call vram_copy
 ld hl,portrait_map
 ld b,1
.prow:
 push bc
 push hl
 ld c,10
 call name_addr
 call vdp_waddr
 pop hl
 ld b,PORTRAIT_W
.pcol:
 ld a,(hl)
 out (VDP_DATA),a
 xor a
 out (VDP_DATA),a
 inc hl
 djnz .pcol
 pop bc
 inc b
 ld a,b
 cp 1+PORTRAIT_W
 jr nz,.prow
 ld hl,portrait_pal
 xor a
 call load_palette16
 ld b,14
 ld c,7
 ld hl,txt_title1
 call print_at
 ld b,15
 ld c,11
 ld hl,txt_title2
 call print_at
 ld b,17
 ld c,13
 ld hl,txt_normal
 call print_at
 ld b,18
 ld c,13
 ld hl,txt_hardcore
 call print_at
 ld b,22
 ld c,6
 ld hl,txt_copy
 call print_at
 ld b,20
 ld c,6
 ld hl,txt_press
 call print_at
 call title_cursor
 call display_on
 ei
 ld a,MUS_TITLE
 call snd_play_music
.loop:
 call wait_vblank
 call read_pad
 ld a,(frame_cnt)
 and 31
 jr nz,.noblink
 di
 ld a,(frame_cnt)
 and 32
 jr z,.show
 ld b,20
 call clear_row
 jr .bdone
.show:
 ld b,20
 ld c,6
 ld hl,txt_press
 call print_at
.bdone:
 ei
.noblink:
 ld a,(pad_new)
 and 3                ; up / down
 jr z,.nosel
 ld a,(title_sel)
 xor 1
 ld (title_sel),a
 ld a,SFX_SELECT
 call snd_sfx
 di
 call title_cursor
 ei
.nosel:
 ld a,(pad_new)
 and $30
 jr z,.loop
 call rand            ; mix in timing
 ld a,(frame_cnt)
 ld hl,(rnd_seed)
 xor l
 ld l,a
 ld (rnd_seed),hl
 ld a,SFX_POWER
 call snd_sfx
 ld a,(title_sel)
 ld (difficulty),a
 ld a,30
 call wait_frames
 jp start_game

title_cursor:
 ld b,17
 ld c,11
 call name_addr
 call vdp_waddr
 ld a,(title_sel)
 or a
 ld a,T_LIFE
 jr z,.a
 xor a
.a:
 out (VDP_DATA),a
 xor a
 out (VDP_DATA),a
 ld b,18
 ld c,11
 call name_addr
 call vdp_waddr
 ld a,(title_sel)
 or a
 ld a,0
 jr z,.b
 ld a,T_LIFE
.b:
 out (VDP_DATA),a
 xor a
 out (VDP_DATA),a
 ret

clear_name_table:
 ld hl,VRAM_NAME
 call vdp_waddr
 ld de,32*24*2
.l:
 xor a
 out (VDP_DATA),a
 dec de
 ld a,d
 or e
 jr nz,.l
 ret

hide_sprites:
 ld hl,VRAM_SAT
 call vdp_waddr
 ld a,$D0
 out (VDP_DATA),a
 ld (sat_y),a
 ret

txt_title1:  db "WILLOW'S FLATULENT",0
txt_title2:  db "ADVENTURE",0
txt_normal:  db "NORMAL",0
txt_hardcore: db "HARDCORE",0
txt_press:   db "PULSA 1 PARA EMPEZAR",0
txt_copy:    db "© 2026 TONY C. WARE",0
