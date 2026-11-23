; =====================================================================
;  player.asm - Willow + shared platform physics
; =====================================================================
player_reset:
 ld ix,player
 ld (ix+E_TYPE),1
 ld (ix+E_STATE),P_PLAY
 ld hl,(cur_level_ptr)
 ; skip enemy list to find willow x
 ld b,(hl)
 inc hl
 ld a,b
 or a
 jr z,.wx
.sk:
 inc hl
 inc hl
 inc hl
 djnz .sk
.wx:
 ld a,(hl)
 ld (ix+E_X),a
 ld (ix+E_Y),168
 xor a
 ld (ix+E_XF),a
 ld (ix+E_YF),a
 ld (ix+E_VX),a
 ld (ix+E_VXF),a
 ld (ix+E_VY),a
 ld (ix+E_VYF),a
 ld (ix+E_DIR),a
 ld (ix+E_W),16
 ld (ix+E_H),16
 ld (ix+E_INV),0
 ld (fart_anim),a
 ret

; ---------------------------------------------------------------------
player_update:
 ld ix,player
 ld a,(ix+E_STATE)
 cp P_DYING
 jp z,player_dying
 ; invulnerability
 ld a,(ix+E_INV)
 or a
 jr z,.noinv
 dec (ix+E_INV)
.noinv:
 ld a,(fart_anim)
 or a
 jr z,.nofa
 dec a
 ld (fart_anim),a
.nofa:
 ld a,(puff_cool)
 or a
 jr z,.nopc
 dec a
 ld (puff_cool),a
.nopc:
 ; ---- horizontal ----
 ld hl,0
 ld a,(pad_now)
 bit PAD_LEFT,a
 jr z,.nl
 ld (ix+E_DIR),1
 ld hl,(willow_spd)
 call neg_hl
 jr .hset
.nl:
 bit PAD_RIGHT,a
 jr z,.hset
 ld (ix+E_DIR),0
 ld hl,(willow_spd)
.hset:
 ld (ix+E_VXF),l
 ld (ix+E_VX),h
 ; ---- jump ----
 ld a,(pad_new)
 bit PAD_B2,a
 jr z,.nj
 bit F_GROUND,(ix+E_FLAGS)
 jr z,.nj
 ; down + jump on a platform: drop through it
 ld a,(pad_now)
 bit PAD_DOWN,a
 jr z,.dojump
 ld a,(ix+E_Y)
 add a,(ix+E_H)
 ld c,a
 ld a,(ix+E_X)
 add a,3
 ld b,a
 call col_at
 cp COL_SOLID
 jr z,.dojump         ; standing on the floor: normal jump
 ld d,a
 ld a,(ix+E_X)
 add a,(ix+E_W)
 sub 4
 ld b,a
 call col_at
 cp COL_SOLID
 jr z,.dojump
 or d
 jr z,.dojump
 inc (ix+E_Y)         ; feet below the platform top -> one-way platform lets her through
 inc (ix+E_Y)
 xor a
 ld (ix+E_VY),a
 ld (ix+E_VYF),a
 res F_GROUND,(ix+E_FLAGS)
 jr .nj
.dojump:
 ld (ix+E_VYF),lo(JUMP_VEL)
 ld (ix+E_VY),hi(JUMP_VEL)
 ld a,SFX_JUMP
 call sfx_low
.nj:
 ; variable jump height
 ld a,(pad_now)
 bit PAD_B2,a
 jr nz,.vj
 ld a,(ix+E_VY)
 bit 7,a
 jr z,.vj
 cp $FE
 jr nc,.vj
 ld (ix+E_VY),$FE
 ld (ix+E_VYF),0
.vj:
 ; ---- fart ----
 ld a,(pad_new)
 bit PAD_B1,a
 jr z,.nf
 ld a,(puff_cool)
 or a
 jr nz,.nf
 call spawn_puff
.nf:
 call ent_physics
 ; walk anim counter
 ld a,(ix+E_VX)
 or (ix+E_VXF)
 jr z,.still
 ld hl,walk_anim
 inc (hl)
 ret
.still:
 xor a
 ld (walk_anim),a
 ret

; play sfx only if nothing more important is sounding
sfx_low:
 push af
 ld hl,(snd_sfx_ptr)
 ld a,h
 or l
 jr nz,.busy
 pop af
 jp snd_sfx
.busy:
 pop af
 ret

neg_hl:
 xor a
 sub l
 ld l,a
 sbc a,a
 sub h
 ld h,a
 ret

; ---------------------------------------------------------------------
; kill willow
player_hit:
 ld ix,player
 ld a,(ix+E_STATE)
 cp P_PLAY
 ret nz
 ld a,(ix+E_INV)
 or a
 ret nz
 ld a,(clear_timer)
 or a
 ret nz
 ld (ix+E_STATE),P_DYING
 res F_GROUND,(ix+E_FLAGS)
 ld (ix+E_TIMER),150
 ld (ix+E_VY),$FD
 ld (ix+E_VYF),0
 ld a,MUS_DEATH
 call snd_play_music
 ret

player_dying:
 dec (ix+E_TIMER)
 jr z,.done
 bit 7,(ix+E_VY)
 jr z,.fall
 ; rising part of the hop: no collision (goes up through platforms)
 ld l,(ix+E_VYF)
 ld h,(ix+E_VY)
 ld de,$0020
 add hl,de
 ld (ix+E_VYF),l
 ld (ix+E_VY),h
 ld e,(ix+E_YF)
 ld d,(ix+E_Y)
 add hl,de
 ld a,h
 cp 16
 jr nc,.yok
 ld h,16
.yok:
 ld (ix+E_YF),l
 ld (ix+E_Y),h
 ret
.fall:
 ; falling: real collision, she lands lying on the platform or the floor
 bit F_GROUND,(ix+E_FLAGS)
 ret nz
 xor a
 ld (ix+E_VX),a
 ld (ix+E_VXF),a
 call ent_physics
 ld a,(ix+E_Y)
 cp 169
 ret c
 ld (ix+E_Y),168
 set F_GROUND,(ix+E_FLAGS)
 ret
.done:
 ; lose a life
 xor a
 ld (pw_atun),a
 ld (pw_pienso),a
 ld (pw_galleta),a
 call apply_powers
 ld hl,hud_dirty
 set 2,(hl)
 set 1,(hl)
 ld a,(lives)
 dec a
 ld (lives),a
 jr nz,.respawn
 ld a,NA_OVER
 ld (next_action),a
 ret
.respawn:
 call kill_vacuum
 call reset_hurry
 ld ix,player
 ld (ix+E_STATE),P_PLAY
 ld (ix+E_INV),150
 ld hl,(cur_level_ptr)
 ld b,(hl)
 inc hl
 ld a,b
 or a
 jr z,.wx
.sk:
 inc hl
 inc hl
 inc hl
 djnz .sk
.wx:
 ld a,(hl)
 ld (ix+E_X),a
 ld (ix+E_Y),168
 xor a
 ld (ix+E_VY),a
 ld (ix+E_VYF),a
 ld a,(last_music)
 jp snd_play_music

; =====================================================================
; ent_physics: IX = entity. gravity, vertical/horizontal movement with
; tile collision. Sets F_GROUND / F_WALL in E_FLAGS.
; =====================================================================
ent_physics:
 res F_WALL,(ix+E_FLAGS)
 ; ---- vertical ----
 ld l,(ix+E_VYF)
 ld h,(ix+E_VY)
 ld de,GRAVITY
 add hl,de
 bit 7,h
 jr nz,.vok
 ld a,h
 cp MAXFALL
 jr c,.vok
 ld hl,MAXFALL*256
.vok:
 ld (ix+E_VYF),l
 ld (ix+E_VY),h
 ld a,(ix+E_Y)
 ld (tmp0),a
 ld e,(ix+E_YF)
 ld d,(ix+E_Y)
 add hl,de
 ld (ix+E_YF),l
 ld (ix+E_Y),h
 res F_GROUND,(ix+E_FLAGS)
 bit 7,(ix+E_VY)
 jr nz,.up
 ; falling: probe below feet
 ld a,(ix+E_Y)
 add a,(ix+E_H)
 ld c,a
 ld a,(ix+E_X)
 add a,3
 ld b,a
 call col_at
 or a
 jr nz,.land
 ld a,(ix+E_X)
 add a,(ix+E_W)
 sub 4
 ld b,a
 call col_at
 or a
 jr z,.vdone
.land:
 ld a,c
 and $F8
 ld d,a               ; row top
 ld a,(tmp0)
 add a,(ix+E_H)
 cp d
 jr z,.doland
 jr nc,.vdone         ; was already below the top -> pass through
.doland:
 ld a,d
 sub (ix+E_H)
 ld (ix+E_Y),a
 xor a
 ld (ix+E_YF),a
 ld (ix+E_VY),a
 ld (ix+E_VYF),a
 set F_GROUND,(ix+E_FLAGS)
 jr .vdone
.up:
 ld a,(ix+E_Y)
 ld c,a
 ld a,(ix+E_X)
 add a,3
 ld b,a
 call col_at
 cp COL_SOLID
 jr z,.bonk
 ld a,(ix+E_X)
 add a,(ix+E_W)
 sub 4
 ld b,a
 call col_at
 cp COL_SOLID
 jr nz,.vdone
.bonk:
 ld a,c
 and $F8
 add a,8
 ld (ix+E_Y),a
 xor a
 ld (ix+E_YF),a
 ld (ix+E_VY),a
 ld (ix+E_VYF),a
.vdone:
 ; ---- horizontal ----
 ld l,(ix+E_VXF)
 ld h,(ix+E_VX)
 ld a,h
 or l
 ret z
 ld e,(ix+E_XF)
 ld d,(ix+E_X)
 add hl,de
 ; h = new x
 bit 7,(ix+E_VX)
 jr nz,.left
 ld a,h
 add a,(ix+E_W)
 dec a
 ld b,a
 call side_solid
 jr nc,.hstore
 ld a,b
 and $F8
 sub (ix+E_W)
 ld h,a
 ld l,0
 set F_WALL,(ix+E_FLAGS)
 jr .hstore
.left:
 ld b,h
 call side_solid
 jr nc,.hstore
 ld a,b
 and $F8
 add a,8
 ld h,a
 ld l,0
 set F_WALL,(ix+E_FLAGS)
.hstore:
 ld (ix+E_XF),l
 ld (ix+E_X),h
 ret

; b = x column pixel; checks entity body rows y+2 and y+H-3 for solid
; returns carry if blocked. preserves hl, b
side_solid:
 push hl
 ld a,(ix+E_Y)
 add a,2
 ld c,a
 call col_at
 cp COL_SOLID
 jr z,.yes
 ld a,(ix+E_Y)
 add a,(ix+E_H)
 sub 3
 ld c,a
 call col_at
 cp COL_SOLID
 jr z,.yes
 pop hl
 or a
 ret
.yes:
 pop hl
 scf
 ret

; b = x pixel, c = y pixel -> a = collision type. preserves bc, de, hl
col_at:
 ld a,c
 cp 192
 jr nc,.solid
 push hl
 and $F8
 ld l,a
 ld h,0
 add hl,hl
 add hl,hl
 ld a,b
 rrca
 rrca
 rrca
 and $1F
 add a,l
 ld l,a
 ld a,h
 add a,hi(colmap)
 ld h,a
 ld a,(hl)
 pop hl
 ret
.solid:
 ld a,COL_SOLID
 ret
