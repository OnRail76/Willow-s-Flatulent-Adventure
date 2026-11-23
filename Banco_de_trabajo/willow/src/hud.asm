; =====================================================================
;  hud.asm - score, lives, power-ups, messages, boss bar
;  row 0: score(1-6) life(8) x(9) n(10) powers(13-15) HI(18-19) hi(21-26) R-S(28-30)
; =====================================================================
; add BCD score: a = low byte (tens/units), c = hundreds byte
add_score:
 push hl
 ld hl,score
 add a,(hl)
 daa
 ld (hl),a
 inc hl
 ld a,c
 adc a,(hl)
 daa
 ld (hl),a
 inc hl
 ld a,0
 adc a,(hl)
 daa
 ld (hl),a
 ld hl,hud_dirty
 set 0,(hl)
 ; extend?
 ld hl,score+2
 ld de,next_extend+2
 ld b,3
.c:
 ld a,(de)
 cp (hl)
 jr c,.ext
 jr nz,.noext
 dec hl
 dec de
 djnz .c
 jr .ext              ; equal -> extend
.noext:
 call update_hiscore
 pop hl
 ret
.ext:
 ; next_extend += 1500
 ld hl,next_extend+1
 ld a,(hl)
 add a,$15
 daa
 ld (hl),a
 inc hl
 ld a,(hl)
 adc a,0
 daa
 ld (hl),a
 ld a,(lives)
 cp 9
 jr nc,.max
 inc a
 ld (lives),a
.max:
 ld hl,hud_dirty
 set 1,(hl)
 ld a,SFX_EXTEND
 call snd_sfx
 ld hl,txt_extend
 ld a,120
 call show_msg
 jr .noext

; ---------------------------------------------------------------------
; called in vblank with interrupts disabled
hud_update:
 ld a,(hud_dirty)
 or a
 ret z
 bit 0,a
 call nz,hud_score
 ld a,(hud_dirty)
 bit 5,a
 call nz,hud_hiscore
 ld a,(hud_dirty)
 bit 1,a
 call nz,hud_lives
 ld a,(hud_dirty)
 bit 2,a
 call nz,hud_powers
 ld a,(hud_dirty)
 bit 6,a
 call nz,hud_stage
 ld a,(hud_dirty)
 and $18
 call nz,hud_row1
 xor a
 ld (hud_dirty),a
 ret

hud_score:
 ld b,0
 ld c,1
 call name_addr
 call vdp_waddr
 ld a,(score+2)
 call print_bcd
 ld a,(score+1)
 call print_bcd
 ld a,(score)
 jp print_bcd

hud_hiscore:
 ld b,0
 ld c,18
 ld hl,txt_hi
 call print_at
 ld b,0
 ld c,21
 call name_addr
 call vdp_waddr
 ld a,(hiscore+2)
 call print_bcd
 ld a,(hiscore+1)
 call print_bcd
 ld a,(hiscore)
 jp print_bcd
txt_hi: db "HI",0

hud_lives:
 ld b,0
 ld c,8
 call name_addr
 call vdp_waddr
 ld a,T_LIFE
 out (VDP_DATA),a
 xor a
 out (VDP_DATA),a
 ld hl,txt_x
 call print_cont
 ld a,(lives)
 inc a
 out (VDP_DATA),a
 xor a
 out (VDP_DATA),a
 ret
txt_x: db "X",0

hud_powers:
 ld b,0
 ld c,13
 call name_addr
 call vdp_waddr
 ld a,(pw_atun)
 or a
 jr z,.a
 ld a,T_I_ATUN
.a:
 out (VDP_DATA),a
 xor a
 out (VDP_DATA),a
 ld a,(pw_pienso)
 or a
 jr z,.b
 ld a,T_I_PIENSO
.b:
 out (VDP_DATA),a
 xor a
 out (VDP_DATA),a
 ld a,(pw_galleta)
 or a
 jr z,.c
 ld a,T_I_GALLETA
.c:
 out (VDP_DATA),a
 xor a
 out (VDP_DATA),a
 ret

hud_stage:
 ld b,0
 ld c,28
 call name_addr
 call vdp_waddr
 ld a,(room_num)
 add a,2
 out (VDP_DATA),a
 xor a
 out (VDP_DATA),a
 ld hl,txt_dash
 call print_cont
 ld a,(screen_num)
 add a,2
 out (VDP_DATA),a
 xor a
 out (VDP_DATA),a
 ret
txt_dash: db "-",0

; row 1: message (centered) or boss bar
hud_row1:
 ld b,1
 call clear_row
 ld hl,(msg_ptr)
 ld a,h
 or l
 jr z,.boss
 ; length
 push hl
 ld b,0
.len:
 ld a,(hl)
 or a
 jr z,.lend
 inc b
 inc hl
 jr .len
.lend:
 ld a,32
 sub b
 srl a
 ld c,a
 ld b,1
 pop hl
 jp print_at
.boss:
 ld a,(boss_active)
 or a
 ret z
 ld b,1
 ld c,4
 ld hl,txt_boss
 call print_at
 ld b,1
 ld c,14
 call name_addr
 call vdp_waddr
 ld a,(boss_maxhp)
 ld b,a
 ld a,(boss_hp)
 ld c,a
.bar:
 ld a,c
 or a
 ld a,T_BAR_E
 jr z,.be
 dec c
 ld a,T_BAR_F
.be:
 out (VDP_DATA),a
 xor a
 out (VDP_DATA),a
 djnz .bar
 ret
