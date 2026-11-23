; =====================================================================
;  objects.asm - gas puffs, items/power-ups, star particles, messages
;  NOTE: routines here must preserve IY (used by callers' loops)
; =====================================================================
spawn_puff:
 ld hl,puffs
 ld b,MAX_PUFF
.f:
 ld a,(hl)
 or a
 jr z,.got
 ld de,PUFF_SIZE
 add hl,de
 djnz .f
 ret
.got:
 ld (hl),1
 inc hl
 ld a,(ix+E_DIR)
 or a
 ld a,(ix+E_X)
 jr nz,.fl
 ; facing right: gas leaves from the rear (left)
 sub 7
 ld (hl),a
 inc hl
 ld a,(ix+E_Y)
 add a,6
 ld (hl),a
 inc hl
 ld (hl),-3
 jr .rest
.fl:
 add a,15
 ld (hl),a
 inc hl
 ld a,(ix+E_Y)
 add a,6
 ld (hl),a
 inc hl
 ld (hl),3
.rest:
 inc hl
 ld a,(puff_range)
 ld (hl),a
 inc hl
 ld a,(pw_atun)
 ld (hl),a
 inc hl
 ld (hl),0
 ld a,14
 ld (fart_anim),a
 ld a,12
 ld (puff_cool),a
 ld a,(pw_atun)
 or a
 ld a,SFX_FART
 jr z,.s
 ld a,SFX_BIGFART
.s:
 jp snd_sfx

puffs_update:
 ld iy,puffs
 ld b,MAX_PUFF
.l:
 push bc
 ld a,(iy+PF_ACT)
 or a
 call nz,puff_one
 pop bc
 ld de,PUFF_SIZE
 add iy,de
 djnz .l
 ret

puff_one:
 inc (iy+PF_ANIM)
 ld a,(iy+PF_X)
 add a,(iy+PF_DX)
 ld (iy+PF_X),a
 dec (iy+PF_DIST)
 jr z,.kill
 ; wall
 add a,4
 ld b,a
 ld a,(iy+PF_Y)
 add a,4
 ld c,a
 call col_at
 cp COL_SOLID
 jr z,.kill
 ; enemies
 ld ix,enemies
 ld b,MAX_ENEMY
.e:
 push bc
 ld a,(ix+E_TYPE)
 or a
 jr z,.en
 cp T_ASPIRA
 jr z,.en
 ld a,(ix+E_STATE)
 cp S_DYING
 jr z,.en
 cp S_ROLL
 jr z,.en
 cp S_APPEAR
 jr z,.en
 call puff_overlap
 jr nc,.en
 pop bc
 ld a,(ix+E_TYPE)
 cp T_LAVADORA
 jr z,.clang
 ld a,(puff_power)
 ld b,(iy+PF_DX)
 call gas_enemy
 jr .kill
.clang:
 ld a,SFX_CLANG
 call snd_sfx
 jr .kill
.en:
 pop bc
 ld de,ENT_SIZE
 add ix,de
 djnz .e
 ret
.kill:
 ld (iy+PF_ACT),0
 ret

; puff (IY, 8x8) vs enemy IX (inset 2) -> carry
puff_overlap:
 ld a,(ix+E_X)
 add a,(ix+E_W)
 sub 2
 ld c,a
 ld a,(iy+PF_X)
 cp c
 jr nc,.no
 add a,8
 ld c,a
 ld a,(ix+E_X)
 add a,2
 cp c
 jr nc,.no
 ld a,(ix+E_Y)
 add a,(ix+E_H)
 sub 2
 ld c,a
 ld a,(iy+PF_Y)
 cp c
 jr nc,.no
 add a,8
 ld c,a
 ld a,(ix+E_Y)
 add a,2
 cp c
 jr nc,.no
 scf
 ret
.no:
 or a
 ret

; ---------------------------------------------------------------------
; items
; drop at kill_x/kill_y
drop_item:
 ld hl,items
 ld b,MAX_ITEM
.f:
 ld a,(hl)
 or a
 jr z,.got
 ld de,ITEM_SIZE
 add hl,de
 djnz .f
 ret
.got:
 call rand
 cp 56
 jr nc,.food
 ; power-up 1..3
 call rand
 and 3
 jr nz,.p
 inc a
.p:
 jr .set
.food:
 call rand
 and 3
 jr nz,.fd
 inc a
.fd:
 add a,3              ; 4..6
.set:
 ld (hl),a
 inc hl
 ld a,(kill_x)
 cp 224
 jr c,.x1
 ld a,224
.x1:
 cp 8
 jr nc,.x2
 ld a,8
.x2:
 ld (hl),a
 inc hl
 ld a,(kill_y)
 cp 176
 jr c,.y1
 ld a,166
.y1:
 cp 24
 jr nc,.y2
 ld a,24
.y2:
 and $FE
 ld (hl),a
 inc hl
 ld (hl),0
 inc hl
 ld (hl),lo(480)
 inc hl
 ld (hl),0            ; ground
 inc hl
 ld (hl),hi(480)      ; timer high
 ret

items_update:
 ld iy,items
 ld b,MAX_ITEM
.l:
 push bc
 ld a,(iy+IT_TYPE)
 or a
 call nz,item_one
 pop bc
 ld de,ITEM_SIZE
 add iy,de
 djnz .l
 ret

item_one:
 ; lifetime (16 bit: IT_TIMER lo, +6 hi)
 ld l,(iy+IT_TIMER)
 ld h,(iy+6)
 dec hl
 ld (iy+IT_TIMER),l
 ld (iy+6),h
 ld a,h
 or l
 jr nz,.alive
 ld (iy+IT_TYPE),0
 ret
.alive:
 ld a,(iy+IT_GROUND)
 or a
 jr nz,.grounded
 ; fall 2 px; land when the bottom edge crosses the top of a platform/floor tile
 ld a,(iy+IT_Y)
 add a,16
 ld e,a               ; e = old bottom (first pixel under the item)
 ld a,(iy+IT_Y)
 add a,2
 ld (iy+IT_Y),a
 add a,16
 ld c,a               ; c = new bottom
 and $F8
 ld d,a               ; d = top of the tile row under the item
 ld a,e
 cp d
 jr z,.probe
 jr nc,.pick          ; already below that tile top: keep falling
.probe:
 ld a,(iy+IT_X)
 add a,3
 ld b,a
 call col_at
 or a
 jr nz,.land
 ld a,(iy+IT_X)
 add a,12
 ld b,a
 call col_at
 or a
 jr z,.pick
.land:
 ld a,d
 sub 16
 ld (iy+IT_Y),a
 ld (iy+IT_GROUND),1
 jr .pick
.grounded:
.pick:
 ld a,(player+E_STATE)
 cp P_PLAY
 ret nz
 ; |dx| < 12 and |dy| < 12
 ld a,(player+E_X)
 sub (iy+IT_X)
 jr nc,.dx
 neg
.dx:
 cp 12
 ret nc
 ld a,(player+E_Y)
 sub (iy+IT_Y)
 jr nc,.dy
 neg
.dy:
 cp 12
 ret nc
 ; collect!
 ld a,(iy+IT_TYPE)
 ld (iy+IT_TYPE),0
 cp IT_SUSHI
 jr nc,.food
 ld hl,pw_atun-1
 ld e,a
 ld d,0
 add hl,de
 ld (hl),1
 call apply_powers
 ld hl,hud_dirty
 set 2,(hl)
 ld a,$10
 ld c,0
 call add_score
 ld a,SFX_POWER
 jp snd_sfx
.food:
 sub IT_SUSHI
 add a,a
 ld e,a
 ld d,0
 ld hl,food_scores
 add hl,de
 ld a,(hl)
 inc hl
 ld c,(hl)
 call add_score
 ld a,SFX_FOOD
 jp snd_sfx
food_scores: db $00,$01, $00,$02, $50,$00

; ---------------------------------------------------------------------
; stars: b=x c=y
spawn_stars:
 push bc
 call .one
 pop bc
 ld a,b
 add a,8
 ld b,a
 ld a,c
 add a,6
 ld c,a
.one:
 ld hl,parts
 ld e,MAX_PART
.f:
 ld a,(hl)
 or a
 jr z,.got
 inc hl
 inc hl
 inc hl
 inc hl
 dec e
 jr nz,.f
 ret
.got:
 ld (hl),24
 inc hl
 ld (hl),b
 inc hl
 ld (hl),c
 inc hl
 ld (hl),0
 ret

parts_update:
 ld hl,parts
 ld b,MAX_PART
.l:
 ld a,(hl)
 or a
 jr z,.n
 dec (hl)
 inc hl
 inc hl
 ld a,(frame_cnt)
 and 1
 jr z,.ny
 dec (hl)
.ny:
 inc hl
 inc (hl)
 inc hl
 djnz .l
 ret
.n:
 inc hl
 inc hl
 inc hl
 inc hl
 djnz .l
 ret

; ---------------------------------------------------------------------
; messages on HUD row 1. hl = text, a = frames (255 = until cleared)
show_msg:
 ld (msg_ptr),hl
 ld (msg_timer),a
 ld hl,hud_dirty
 set 3,(hl)
 ret

msg_update:
 ld a,(msg_timer)
 or a
 ret z
 cp 255
 ret z
 dec a
 ld (msg_timer),a
 ret nz
 ld hl,0
 ld (msg_ptr),hl
 ld hl,hud_dirty
 set 3,(hl)
 ret
