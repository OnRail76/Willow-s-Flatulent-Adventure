; =====================================================================
;  game.asm - game flow: start, screens, main loop, clear, over, ending
; =====================================================================
NA_NONE     equ 0
NA_NEXT     equ 1
NA_OVER     equ 2

start_game:
 ld a,GS_GAME
 ld (game_state),a
 xor a
 ld (score),a
 ld (score+1),a
 ld (score+2),a
 ld (loop_num),a
 ld (room_num),a
 ld (screen_num),a
 ld (pw_atun),a
 ld (pw_pienso),a
 ld (pw_galleta),a
 ld (next_extend),a
 ld (next_extend+2),a
 ld a,$10
 ld (next_extend+1),a        ; first extend at 1000
 ld a,3
 ld (lives),a
 call apply_powers
new_screen:
 call calc_speed
 ld a,(screen_num)
 or a
 call z,room_intro
 call setup_screen
game_loop:
 call wait_vblank
 di
 call upload_sat
 call hud_update
 ei
 call read_pad
 ld a,(paused)
 or a
 jr nz,.paused
 ld a,(pause_state)
 or a
 call nz,unpause
 call game_tick
 call build_sprites
 ld a,(next_action)
 cp NA_NEXT
 jr z,.next
 cp NA_OVER
 jp z,game_over
 jr game_loop
.paused:
 ld a,(pause_state)
 or a
 jr nz,game_loop
 ld a,1
 ld (pause_state),a
 xor a
 ld (snd_mus_on),a
 call snd_silence
 ld hl,txt_pause
 ld a,255
 call show_msg
 jr game_loop
.next:
 ; advance screen / room
 ld a,(boss_dead)
 or a
 jp nz,ending
 ld a,(screen_num)
 inc a
 cp 5
 jr c,.sok
 ld a,(room_num)
 inc a
 and 3
 ld (room_num),a
 xor a
.sok:
 ld (screen_num),a
 jp new_screen

unpause:
 xor a
 ld (pause_state),a
 ld a,1
 ld (snd_mus_on),a
 xor a
 ld (msg_timer),a
 ld hl,0
 ld (msg_ptr),hl
 ld hl,hud_dirty
 set 3,(hl)
 ret

; enemy speed level = loop + difficulty (max 4)
calc_speed:
 ld a,(loop_num)
 ld b,a
 ld a,(difficulty)
 add a,b
 cp 5
 jr c,.ok
 ld a,4
.ok:
 ld (enemy_speed),a
 ret

; set willow speed / puff range from powerups
apply_powers:
 ld hl,$0150
 ld a,(pw_pienso)
 or a
 jr z,.s
 ld hl,$0200
.s:
 ld (willow_spd),hl
 ld a,14
 ld b,a
 ld a,(pw_galleta)
 or a
 ld a,b
 jr z,.r
 ld a,26
.r:
 ld (puff_range),a
 ld a,(pw_atun)
 inc a
 ld (puff_power),a
 ret

; ---------------------------------------------------------------------
; room title card
; ---------------------------------------------------------------------
room_intro:
 di
 call display_off
 call clear_name_table
 call hide_sprites
 ld hl,room_pals
 xor a
 call load_palette16
 ld a,(room_num)
 add a,a
 ld e,a
 ld d,0
 ld hl,room_names
 add hl,de
 ld e,(hl)
 inc hl
 ld d,(hl)
 ex de,hl
 ld b,10
 ld c,9
 call print_at
 ld a,(loop_num)
 or a
 jr z,.nolap
 ld b,13
 ld c,12
 ld hl,txt_vuelta
 call print_at
 ld a,(loop_num)
 inc a
 add a,1             ; font digit = value+1
 out (VDP_DATA),a
 xor a
 out (VDP_DATA),a
.nolap:
 ld a,(room_num)
 cp 3
 jr nz,.nb
 ld b,15
 ld c,8
 ld hl,txt_cuidado
 call print_at
 ld b,16
 ld c,11
 ld hl,txt_lav2
 call print_at
.nb:
 call display_on
 ei
 ld a,MUS_READY
 call snd_play_music
 ld a,150
 call wait_button
 ret

room_names:
 dw txt_r0, txt_r1, txt_r2, txt_r3
txt_r0: db " EL DORMITORIO",0
txt_r1: db "  EL COMEDOR",0
txt_r2: db "   LA COCINA",0
txt_r3: db "    EL BAÑO",0
txt_vuelta: db "VUELTA ",0
txt_cuidado: db "¡CUIDADO CON LA",0
txt_pause:  db "PAUSA",0
txt_lav2:   db "LAVADORA!",0
txt_ready:  db "¡PREPARADA!",0
txt_hurry:  db "¡DATE PRISA!",0
txt_clear:  db "¡GENIAL!",0
txt_over:   db "FIN DE LA PARTIDA",0
txt_extend: db "¡VIDA EXTRA!",0
txt_boss:   db "LAVADORA",0

; ---------------------------------------------------------------------
; build & show a screen
; ---------------------------------------------------------------------
setup_screen:
 di
 call display_off
 call hide_sprites
 ; room tiles
 ld a,(room_num)
 ld l,a
 ld h,0
 ld de,ROOM_TILE_COUNT*32
 call mul16           ; hl = room * 480
 ld de,room_tiles
 add hl,de
 push hl
 ld hl,ROOM_TILE_BASE*32
 call vdp_waddr
 pop hl
 ld de,ROOM_TILE_COUNT*32
 call vram_copy
 ld a,(room_num)
 add a,a
 add a,a
 add a,a
 add a,a
 ld e,a
 ld d,0
 ld hl,room_pals
 add hl,de
 xor a
 call load_palette16
 call build_map
 ld hl,VRAM_NAME
 call vdp_waddr
 ld hl,namebuf
 ld de,32*24*2
 call vram_copy
 call clear_objects
 call spawn_from_level
 call player_reset
 xor a
 ld (next_action),a
 ld (clear_timer),a
 ld (hurry_state),a
 ld (boss_dead),a
 ld (msg_timer),a
 ld (shake),a
 ld (puff_cool),a
 ld (paused),a
 ld (pause_state),a
 call reset_hurry
 ld a,$FF
 ld (hud_dirty),a
 call hud_update
 call display_on
 ei
 ld a,MUS_READY
 call snd_play_music
 ld a,90
 ld (ready_timer),a
 ld hl,txt_ready
 ld a,90
 call show_msg
 call build_sprites
 ret

reset_hurry:
 ld hl,45*60
 ld a,(difficulty)
 or a
 jr z,.n
 ld hl,30*60
.n:
 ld (hurry_timer),hl
 xor a
 ld (hurry_state),a
 ret

; hl * de -> hl (small values)
mul16:
 ld b,h
 ld c,l
 ld hl,0
 ld a,b
 or c
 ret z
.l:
 add hl,de
 dec bc
 ld a,b
 or c
 jr nz,.l
 ret

; level pointer -> hl
level_ptr:
 ld a,(room_num)
 ld b,a
 add a,a
 add a,a
 add a,b               ; *5
 ld b,a
 ld a,(screen_num)
 add a,b
 add a,a
 ld e,a
 ld d,0
 ld hl,level_table
 add hl,de
 ld e,(hl)
 inc hl
 ld d,(hl)
 ex de,hl
 ret

; ---------------------------------------------------------------------
; namebuf + colmap
; ---------------------------------------------------------------------
build_map:
 ld hl,namebuf
 ld de,colmap
 ld b,0               ; row
.row:
 ld c,0
.col:
 ; default
 ld a,b
 cp 2
 jr c,.hud
 jr z,.floor
 cp 23
 jr z,.floor
 ld a,c
 or a
 jr z,.side
 cp 31
 jr z,.side
 ; wallpaper
 ld a,b
 add a,a
 add a,b
 ld (tmp2),a
 ld a,c
 add a,a
 add a,a
 add a,c
 push hl
 ld hl,tmp2
 add a,(hl)
 pop hl
 and 7
 ld a,RT_WALLA
 jr nz,.put0
 ld a,RT_WALLB
.put0:
 ld (hl),a
 xor a
 ld (de),a
 jr .next
.hud:
 xor a
 ld (hl),a
 ld (de),a
 jr .next
.floor:
 ld a,RT_FLOOR
 jr .solid
.side:
 ld a,RT_SIDE
.solid:
 ld (hl),a
 ld a,COL_SOLID
 ld (de),a
.next:
 inc hl
 ld (hl),0
 inc hl
 inc de
 inc c
 ld a,c
 cp 32
 jr nz,.col
 inc b
 ld a,b
 cp 24
 jr nz,.row
 ; ---- level data ----
 call level_ptr
 ld b,(hl)            ; platforms
 inc hl
 ld a,b
 or a
 jr z,.nop
.plat:
 push bc
 ld b,(hl)            ; row
 inc hl
 ld c,(hl)            ; col
 inc hl
 ld a,(hl)            ; len
 inc hl
 push hl
 ld (tmp0),a
 ld a,c
 ld (tmp1),a          ; start col
.pl:
 ; tile choice
 ld a,(tmp1)
 cp c
 jr nz,.notfirst
 cp 2
 jr c,.notfirst
 ld a,RT_PL
 jr .ptile
.notfirst:
 ld a,(tmp0)
 cp 1
 jr nz,.mid
 ld a,c
 cp 30
 jr z,.mid
 ld a,RT_PR
 jr .ptile
.mid:
 ld a,RT_PM
.ptile:
 push af
 call map_index       ; hl = index (b,c)
 pop af
 push hl
 add hl,hl
 ld de,namebuf
 add hl,de
 ld (hl),a
 pop hl
 ld de,colmap
 add hl,de
 ld (hl),COL_PLAT
 inc c
 ld a,(tmp0)
 dec a
 ld (tmp0),a
 jr nz,.pl
 pop hl
 pop bc
 djnz .plat
.nop:
 ; decorations
 ld b,(hl)
 inc hl
 ld a,b
 or a
 jr z,.nod
.deco:
 push bc
 ld b,(hl)
 inc hl
 ld c,(hl)
 inc hl
 ld a,(hl)
 inc hl
 push hl
 or a
 ld a,RT_D0
 jr z,.dk
 ld a,RT_D4
.dk:
 ld (tmp0),a
 call deco_put
 inc c
 call deco_put
 dec c
 inc b
 call deco_put
 inc c
 call deco_put
 pop hl
 pop bc
 djnz .deco
.nod:
 ld (cur_level_ptr),hl   ; -> enemy list
 ret

deco_put:
 push bc
 call map_index
 add hl,hl
 ld de,namebuf
 add hl,de
 ld a,(tmp0)
 ld (hl),a
 inc a
 ld (tmp0),a
 pop bc
 ret

; b=row c=col -> hl = row*32+col
map_index:
 ld l,b
 ld h,0
 add hl,hl
 add hl,hl
 add hl,hl
 add hl,hl
 add hl,hl
 ld a,l
 add a,c
 ld l,a
 ret

clear_objects:
 ld hl,player
 ld de,player+1
 ld bc,ENT_SIZE*(MAX_ENEMY+1)+PUFF_SIZE*MAX_PUFF+ITEM_SIZE*MAX_ITEM+PART_SIZE*MAX_PART-1
 ld (hl),0
 ldir
 xor a
 ld (boss_active),a
 ret

; ---------------------------------------------------------------------
; per-frame game logic
; ---------------------------------------------------------------------
game_tick:
 ld a,(ready_timer)
 or a
 jr z,.play
 dec a
 ld (ready_timer),a
 ret nz
 ; start music
 ld a,(boss_active)
 or a
 ld a,MUS_MAIN
 jr z,.m
 ld a,MUS_BOSS
.m:
 ld (last_music),a
 call snd_play_music
 ld a,1
 ld (msg_timer),a
 ret
.play:
 call player_update
 call puffs_update
 call enemies_update
 call items_update
 call parts_update
 call hurry_update
 call check_clear
 call msg_update
 ld a,(shake)
 or a
 ret z
 dec a
 ld (shake),a
 ret

check_clear:
 ld a,(clear_timer)
 or a
 jr nz,.counting
 ld a,(enemies_left)
 or a
 ret nz
 ld a,(player+E_STATE)
 cp P_PLAY
 ret nz
 ; screen cleared!
 ld a,200
 ld (clear_timer),a
 call kill_vacuum
 ld a,MUS_CLEAR
 call snd_play_music
 ld hl,txt_clear
 ld a,150
 jp show_msg
.counting:
 dec a
 ld (clear_timer),a
 ret nz
 ld a,NA_NEXT
 ld (next_action),a
 ret

; ---------------------------------------------------------------------
game_over:
 call snd_stop_music
 ld a,MUS_OVER
 call snd_play_music
 di
 ld b,12
 ld c,7
 ld hl,txt_over
 call print_at
 ei
 call update_hiscore
 ld a,240
 call wait_button
 jp title_screen

update_hiscore:
 ld hl,score+2
 ld de,hiscore+2
 ld b,3
.c:
 ld a,(de)
 cp (hl)
 jr c,.new
 ret nz
 dec hl
 dec de
 djnz .c
 ret
.new:
 ld hl,score
 ld de,hiscore
 ld bc,3
 ldir
 ld hl,hud_dirty
 set 5,(hl)
 ret

; ---------------------------------------------------------------------
; ending after defeating La Lavadora
; ---------------------------------------------------------------------
ending:
 di
 call display_off
 call clear_name_table
 call hide_sprites
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
 ld c,4
 ld hl,txt_end1
 call print_at
 ld b,15
 ld c,12
 ld hl,txt_end2
 call print_at
 ld b,17
 ld c,6
 ld hl,txt_end3
 call print_at
 ld b,18
 ld c,8
 ld hl,txt_end5
 call print_at
 ld b,21
 ld c,6
 ld hl,txt_end4
 call print_at
 call display_on
 ei
 ld a,MUS_ENDING
 call snd_play_music
 ld a,0
 call wait_button
 ; next lap
 ld a,(loop_num)
 inc a
 cp 9
 jr c,.l
 ld a,9
.l:
 ld (loop_num),a
 xor a
 ld (room_num),a
 ld (screen_num),a
 ld (boss_dead),a
 ld a,GS_GAME
 ld (game_state),a
 jp new_screen

txt_end1: db "¡LA CASA VUELVE A ESTAR",0
txt_end2: db "EN PAZ!",0
txt_end3: db "WILLOW SE HA GANADO",0
txt_end5: db "UNA BUENA SIESTA",0
txt_end4: db "PULSA 1: OTRA VUELTA",0
