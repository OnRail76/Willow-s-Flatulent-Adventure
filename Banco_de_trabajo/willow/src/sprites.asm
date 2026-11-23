; =====================================================================
;  sprites.asm - build the SAT buffer each frame, upload in vblank
; =====================================================================
upload_sat:
 ld hl,VRAM_SAT
 call vdp_waddr
 ld hl,sat_y
 ld bc,64*256+VDP_DATA
 otir
 ld hl,VRAM_SAT+128
 call vdp_waddr
 ld hl,sat_xn
 ld bc,128*256+VDP_DATA
 otir
 ; screen shake via vertical scroll
 ld a,(shake)
 and 2
 ld b,9
 jp vdp_reg

; b = x, c = y, a = tile (sprite tile index)
add_spr8:
 ld e,a
 ld a,c
 cp 192
 ret nc
 ld a,(spr_count)
 cp 64
 ret nc
 push hl
 ld l,a
 ld h,hi(sat_y)
 ld a,c
 dec a
 ld (hl),a
 ld a,l
 add a,a
 add a,lo(sat_xn)
 ld l,a
 ld (hl),b
 inc l
 ld (hl),e
 ld hl,spr_count
 inc (hl)
 pop hl
 ret

; 16x16 metasprite: b=x c=y a=tile
meta16:
 ld d,a
 call add_spr8
 ld a,b
 add a,8
 ld b,a
 ld a,d
 inc a
 call add_spr8
 ld a,c
 add a,8
 ld c,a
 ld a,d
 add a,3
 call add_spr8
 ld a,b
 sub 8
 ld b,a
 ld a,d
 add a,2
 call add_spr8
 ld a,c
 sub 8
 ld c,a
 ret

; 32x32 metasprite (4x4 tiles row-major): b=x c=y a=tile
meta32:
 ld d,a
 ld (tmp0),a
 push bc
 ld h,4
.row:
 push bc
 ld l,4
.col:
 ld a,(tmp0)
 push hl
 call add_spr8
 pop hl
 ld a,(tmp0)
 inc a
 ld (tmp0),a
 ld a,b
 add a,8
 ld b,a
 dec l
 jr nz,.col
 pop bc
 ld a,c
 add a,8
 ld c,a
 dec h
 jr nz,.row
 pop bc
 ret

; ---------------------------------------------------------------------
build_sprites:
 xor a
 ld (spr_count),a
 call draw_willow
 call draw_items
 call draw_puffs
 call draw_parts
 call draw_enemies
 ; terminator
 ld a,(spr_count)
 cp 64
 ret nc
 ld l,a
 ld h,hi(sat_y)
 ld (hl),$D0
 ret

draw_willow:
 ld ix,player
 ld a,(ix+E_TYPE)
 or a
 ret z
 ld a,(ix+E_INV)
 or a
 jr z,.vis
 ld a,(frame_cnt)
 and 2
 ret nz
.vis:
 ld a,(ix+E_STATE)
 cp P_DYING
 ld a,SPR_W_DEAD_R
 jr z,.dir
 ld a,(fart_anim)
 or a
 ld a,SPR_W_FART_R
 jr nz,.dir
 bit F_GROUND,(ix+E_FLAGS)
 ld a,SPR_W_JUMP_R
 jr z,.dir
 ld a,(walk_anim)
 or a
 ld a,SPR_W_STAND_R
 jr z,.dir
 ld a,(walk_anim)
 rrca
 rrca
 rrca
 and 3
 ld e,a
 ld d,0
 ld hl,walk_frames
 add hl,de
 ld a,(hl)
.dir:
 ld e,a
 ld a,(ix+E_DIR)
 or a
 ld a,e
 jr z,.r
 add a,SPR_W_STAND_L-SPR_W_STAND_R
.r:
 ld b,(ix+E_X)
 ld c,(ix+E_Y)
 jp meta16
walk_frames: db SPR_W_WALK1_R, SPR_W_STAND_R, SPR_W_WALK2_R, SPR_W_STAND_R

draw_items:
 ld iy,items
 ld b,MAX_ITEM
.l:
 push bc
 ld a,(iy+IT_TYPE)
 or a
 jr z,.n
 ; blink when expiring
 ld a,(iy+6)
 or a
 jr nz,.v
 ld a,(iy+IT_TIMER)
 cp 120
 jr nc,.v
 ld a,(frame_cnt)
 and 4
 jr nz,.n
.v:
 ld a,(iy+IT_TYPE)
 dec a
 add a,a
 add a,a
 add a,SPR_ATUN
 ld b,(iy+IT_X)
 ld c,(iy+IT_Y)
 call meta16
.n:
 pop bc
 ld de,ITEM_SIZE
 add iy,de
 djnz .l
 ret

draw_puffs:
 ld iy,puffs
 ld b,MAX_PUFF
.l:
 push bc
 ld a,(iy+PF_ACT)
 or a
 jr z,.n
 ld a,(iy+PF_ANIM)
 rrca
 rrca
 and 1
 ld e,a
 ld a,(iy+PF_BIG)
 or a
 ld a,SPR_PUFF1
 jr z,.s
 ld a,SPR_PUFFBIG1
.s:
 add a,e
 ld b,(iy+PF_X)
 ld c,(iy+PF_Y)
 call add_spr8
.n:
 pop bc
 ld de,PUFF_SIZE
 add iy,de
 djnz .l
 ret

draw_parts:
 ld hl,parts
 ld b,MAX_PART
.l:
 ld a,(hl)
 or a
 jr z,.n
 push hl
 push bc
 inc hl
 ld b,(hl)
 inc hl
 ld c,(hl)
 inc hl
 ld a,(hl)
 rrca
 rrca
 and 1
 add a,SPR_STAR1
 call add_spr8
 pop bc
 pop hl
.n:
 inc hl
 inc hl
 inc hl
 inc hl
 djnz .l
 ret

; enemies, starting at a rotating index for flicker fairness
draw_enemies:
 ld a,(spr_rot)
 inc a
 and 7
 ld (spr_rot),a
 ld (tmp1),a
 ld a,MAX_ENEMY
 ld (tmp2),a
.l:
 ld a,(tmp1)
 add a,a
 add a,a
 add a,a
 add a,a
 add a,a              ; *32
 ld e,a
 ld d,0
 ld ix,enemies
 add ix,de
 ld a,(ix+E_TYPE)
 or a
 call nz,draw_enemy
 ld a,(tmp1)
 inc a
 and 7
 ld (tmp1),a
 ld hl,tmp2
 dec (hl)
 jr nz,.l
 ret

draw_enemy:
 ld b,(ix+E_X)
 ld c,(ix+E_Y)
 cp T_LAVADORA
 jp z,draw_boss
 cp T_ASPIRA
 jp z,.asp
 ld a,(ix+E_STATE)
 cp S_APPEAR
 jr nz,.na
 ld a,(frame_cnt)
 and 4
 ret nz
 jr .body
.na:
 cp S_BALL
 jr z,.ball
 cp S_ROLL
 jr z,.roll
 cp S_DYING
 jr z,.body
 ; normal: partial gas cloud overlay on top priority
 ld a,(ix+E_TUFO)
 or a
 jr z,.body
 push bc
 ld a,c
 add a,8
 ld c,a
 ld a,(frame_cnt)
 rrca
 rrca
 rrca
 and 1
 add a,a
 add a,SPR_CLOUD_LOW1
 ld d,a
 call add_spr8
 ld a,b
 add a,8
 ld b,a
 ld a,d
 inc a
 call add_spr8
 pop bc
.body:
 ld a,(ix+E_TYPE)
 cp T_BOLA
 jr nz,.esc
 ld a,(frame_cnt)
 add a,(ix+E_X)
 rrca
 rrca
 rrca
 and 1
 add a,a
 add a,a
 add a,SPR_BOLA1
 jp meta16
.esc:
 ld a,(frame_cnt)
 rrca
 rrca
 rrca
 and 1
 add a,a
 add a,a
 bit F_BALD,(ix+E_FLAGS)
 jr z,.full
 add a,SPR_ESCB1
 jp meta16
.full:
 add a,SPR_ESC1
 jp meta16
.ball:
 ; wobble when about to break free
 ld a,(ix+E_TUFOT)
 cp 60
 ld a,0
 jr nc,.bf
 ld a,(frame_cnt)
 rrca
 rrca
 and 1
.bf:
 jr .bdraw
.roll:
 ld a,(frame_cnt)
 rrca
 and 1
.bdraw:
 add a,a
 add a,a
 add a,SPR_BALL1
 jp meta16
.asp:
 ld a,(ix+E_ANIM)
 rrca
 rrca
 rrca
 and 1
 add a,a
 add a,a
 ld e,a
 ld a,(ix+E_DIR)
 or a
 ld a,SPR_ASP1_R
 jr z,.ar
 ld a,SPR_ASP1_L
.ar:
 add a,e
 jp meta16

draw_boss:
 ld a,(ix+E_STATE)
 cp S_APPEAR
 jr nz,.v
 ld a,(frame_cnt)
 and 4
 ret nz
.v:
 ld a,(ix+E_INV)
 or a
 jr nz,.hit
 ld a,(ix+E_STATE)
 cp S_DYING
 jr nz,.norm
 ld a,(frame_cnt)
 and 2
 ret nz
.hit:
 ld a,SPR_LAV_HIT
 jp meta32
.norm:
 ld a,(ix+E_ANIM)
 and 16
 ld a,SPR_LAV1
 jr z,.f
 ld a,SPR_LAV2
.f:
 jp meta32
