; =====================================================================
;  enemy.asm - Bola, Escoba, gassed balls, La Lavadora, la Aspiradora
; =====================================================================
spawn_from_level:
 ld hl,(cur_level_ptr)
 ld b,(hl)
 inc hl
 ld a,b
 or a
 ret z
.l:
 push bc
 ld a,(hl)
 inc hl
 ld d,(hl)            ; x
 inc hl
 ld e,(hl)            ; y
 inc hl
 push hl
 call spawn_enemy
 pop hl
 pop bc
 djnz .l
 ret

; a = type, d = x, e = y -> IX = new enemy (carry set if no slot)
spawn_enemy:
 ld c,a
 ld ix,enemies
 ld b,MAX_ENEMY
.f:
 ld a,(ix+E_TYPE)
 or a
 jr z,.got
 push de
 ld de,ENT_SIZE
 add ix,de
 pop de
 djnz .f
 scf
 ret
.got:
 push ix
 pop hl
 push de
 ld d,h
 ld e,l
 inc de
 ld (hl),0
 push bc
 ld bc,ENT_SIZE-1
 ldir
 pop bc
 pop de
 ld (ix+E_TYPE),c
 ld (ix+E_X),d
 ld (ix+E_Y),e
 ld (ix+E_STATE),S_APPEAR
 ld (ix+E_TIMER),60
 ld (ix+E_W),16
 ld (ix+E_H),16
 ; face willow-ish: left half -> go right
 ld a,d
 cp 128
 ld a,0
 jr c,.dir
 inc a
.dir:
 ld (ix+E_DIR),a
 ld a,c
 cp T_LAVADORA
 jr nz,.nb
 ld (ix+E_W),32
 ld (ix+E_H),32
 ld a,6
 ld b,a
 ld a,(difficulty)
 or a
 ld a,b
 jr z,.hp
 ld a,8
.hp:
 ld (ix+E_HP),a
 ld (boss_hp),a
 ld (boss_maxhp),a
 ld a,1
 ld (boss_active),a
 ld (ix+E_TIMER),90
 ld hl,hud_dirty
 set 4,(hl)
.nb:
 or a
 ret

; ---------------------------------------------------------------------
enemies_update:
 xor a
 ld (enemies_left),a
 ld (bolas_alive),a
 ld ix,enemies
 ld b,MAX_ENEMY
.l:
 push bc
 ld a,(ix+E_TYPE)
 or a
 call nz,enemy_one
 pop bc
 ld de,ENT_SIZE
 add ix,de
 djnz .l
 ret

enemy_one:
 ; count living enemies
 cp T_ASPIRA
 jr z,.nc
 ld c,a
 ld a,(ix+E_STATE)
 cp S_DYING
 jr z,.nc
 ld hl,enemies_left
 inc (hl)
 ld a,c
 cp T_BOLA
 jr nz,.nc
 ld hl,bolas_alive
 inc (hl)
.nc:
 ld a,(ix+E_TYPE)
 cp T_LAVADORA
 jp z,boss_update
 cp T_ASPIRA
 jp z,vacuum_update
 ld a,(ix+E_STATE)
 cp S_APPEAR
 jr z,st_appear
 cp S_NORMAL
 jp z,st_normal
 cp S_BALL
 jp z,st_ball
 cp S_ROLL
 jp z,st_roll
 jp st_dying

st_appear:
 dec (ix+E_TIMER)
 ret nz
 ld (ix+E_STATE),S_NORMAL
 ret

; ---------------------------------------------------------------------
st_normal:
 ld a,(ix+E_TUFO)
 or a
 jr z,.free
 ; partially gassed: frozen, decays
 xor a
 ld (ix+E_VX),a
 ld (ix+E_VXF),a
 call ent_physics
 call tufo_decay
 jp touch_player
.free:
 ld a,(ix+E_TYPE)
 cp T_BOLA
 jr nz,.esc
 call ai_bola
 jp touch_player
.esc:
 call ai_escoba
 jp touch_player

tufo_decay:
 dec (ix+E_TUFOT)
 ret nz
 ld (ix+E_TUFOT),TUFO_DECAY
 dec (ix+E_TUFO)
 ret

; speed for current enemy: hl = base + enemy_speed * step
; in: hl = base, de = step
speed_calc:
 ld a,(enemy_speed)
 or a
 ret z
.l:
 add hl,de
 dec a
 jr nz,.l
 ret

set_vx_dir:            ; hl = speed, uses E_DIR
 ld a,(ix+E_DIR)
 or a
 jr z,.r
 call neg_hl
.r:
 ld (ix+E_VXF),l
 ld (ix+E_VX),h
 ret

ai_bola:
 ld hl,$00E0
 ld de,$0030
 call speed_calc
 call set_vx_dir
 call ent_physics
 bit F_WALL,(ix+E_FLAGS)
 jr z,.nw
 ld a,(ix+E_DIR)
 xor 1
 ld (ix+E_DIR),a
.nw:
 bit F_GROUND,(ix+E_FLAGS)
 ret z
 ; bounce
 call rand
 cp 40
 jr c,.big
 ld (ix+E_VY),$FD
 ld (ix+E_VYF),$A0
 ret
.big:
 ld (ix+E_VY),hi(JUMP_VEL)
 ld (ix+E_VYF),lo(JUMP_VEL)
 ret

ai_escoba:
 ld hl,$00A0
 ld de,$0028
 call speed_calc
 bit F_BALD,(ix+E_FLAGS)
 jr z,.nb
 srl h
 rr l
.nb:
 bit F_GROUND,(ix+E_FLAGS)
 jr z,.move
 ; on ground: occasionally re-aim at willow
 ld a,(frame_cnt)
 add a,(ix+E_X)
 and 63
 jr nz,.noaim
 ld a,(player+E_X)
 cp (ix+E_X)
 ld a,0
 jr nc,.aim
 inc a
.aim:
 ld (ix+E_DIR),a
.noaim:
 ; jump if willow is above
 ld a,(player+E_Y)
 add a,12
 cp (ix+E_Y)
 jr nc,.nojump
 push hl
 call rand
 pop hl
 cp 6
 jr nc,.nojump
 ld (ix+E_VY),hi(JUMP_VEL)
 ld (ix+E_VYF),lo(JUMP_VEL)
 jr .move
.nojump:
 ; edge check ahead
 push hl
 ld a,(ix+E_DIR)
 or a
 ld a,(ix+E_X)
 jr nz,.el
 add a,16
 jr .ec
.el:
 sub 1
.ec:
 ld b,a
 ld a,(ix+E_Y)
 add a,16
 ld c,a
 call col_at
 pop hl
 or a
 jr nz,.move
 ; no floor ahead: drop only if willow is below
 ld a,(player+E_Y)
 sub 8
 cp (ix+E_Y)
 jr nc,.move
 ld a,(ix+E_DIR)
 xor 1
 ld (ix+E_DIR),a
.move:
 call set_vx_dir
 call ent_physics
 bit F_WALL,(ix+E_FLAGS)
 ret z
 ld a,(ix+E_DIR)
 xor 1
 ld (ix+E_DIR),a
 ret

; ---------------------------------------------------------------------
; hit by a puff: a = power, b = puff dx (signed)
gas_enemy:
 ld c,a
 ld a,(ix+E_STATE)
 cp S_BALL
 jr z,.kick
 cp S_NORMAL
 ret nz
 ld a,(ix+E_TYPE)
 cp T_ESCOBA
 jr nz,.nb
 set F_BALD,(ix+E_FLAGS)
.nb:
 ld a,(ix+E_TUFO)
 add a,c
 ld (ix+E_TUFO),a
 ld (ix+E_TUFOT),TUFO_DECAY+60
 ld c,a
 call tufo_max
 cp c
 jr z,.full
 jr c,.full
 ld a,SFX_GAS
 jp snd_sfx
.full:
 ld (ix+E_TUFO),a
 ld (ix+E_STATE),S_BALL
 ld (ix+E_TUFOT),TUFO_DECAY+120
 ld a,SFX_GAS
 jp snd_sfx
.kick:
 ld a,b
 rlca
 and 1                ; dx negative -> dir 1
 jp start_roll

; a = gas needed for current enemy
tufo_max:
 ld a,(ix+E_TYPE)
 cp T_BOLA
 ld a,2
 ret z
 ld a,3
 ret

; a = direction
start_roll:
 ld (ix+E_DIR),a
 ld (ix+E_STATE),S_ROLL
 ld (ix+E_BOUNCE),0
 ld (ix+E_COMBO),0
 ld (ix+E_TIMER),0
 ld a,SFX_KICK
 jp snd_sfx

; ---------------------------------------------------------------------
st_ball:
 xor a
 ld (ix+E_VX),a
 ld (ix+E_VXF),a
 call ent_physics
 ; recover?
 dec (ix+E_TUFOT)
 jr nz,.stay
 ld (ix+E_STATE),S_NORMAL
 dec (ix+E_TUFO)
 ld (ix+E_TUFOT),TUFO_DECAY
 ret
.stay:
 ; kicked by willow touching it
 ld iy,player
 ld a,(iy+E_STATE)
 cp P_PLAY
 ret nz
 call overlap_player
 ret nc
 ld a,(player+E_X)
 cp (ix+E_X)
 ld a,0
 jr c,.r
 inc a
.r:
 jp start_roll

; ---------------------------------------------------------------------
st_roll:
 ld h,ROLL_SPEED
 ld l,0
 call set_vx_dir
 call ent_physics
 bit F_WALL,(ix+E_FLAGS)
 jr z,.nw
 ld a,(ix+E_DIR)
 xor 1
 ld (ix+E_DIR),a
 inc (ix+E_BOUNCE)
 ld a,SFX_BOUNCE
 call sfx_low
 ld a,(ix+E_BOUNCE)
 cp 5
 jr nc,.explode
.nw:
 inc (ix+E_TIMER)
 ld a,(ix+E_TIMER)
 cp 240
 jr nc,.explode
 ; hit other enemies
 call roll_hits
 ret
.explode:
 jp kill_rolled

; check rolling ball (IX) against all other enemies
roll_hits:
 ld iy,enemies
 ld b,MAX_ENEMY
.l:
 push bc
 push iy
 pop hl
 push ix
 pop de
 or a
 sbc hl,de
 jr z,.next           ; self
 ld a,(iy+E_TYPE)
 or a
 jr z,.next
 cp T_ASPIRA
 jr z,.next
 call overlap_iy
 jr nc,.next
 ld a,(iy+E_TYPE)
 cp T_LAVADORA
 jr z,.boss
 ld a,(iy+E_STATE)
 cp S_DYING
 jr z,.next
 cp S_ROLL
 jr z,.next
 cp S_BALL
 jr z,.chain
 ; normal / appearing enemy -> dies
 inc (ix+E_COMBO)
 ld a,(ix+E_COMBO)
 push ix
 push iy
 pop ix
 call kill_enemy
 pop ix
 jr .next
.chain:
 ld a,(ix+E_DIR)
 ld (iy+E_DIR),a
 ld (iy+E_STATE),S_ROLL
 ld (iy+E_BOUNCE),0
 ld (iy+E_TIMER),0
 ld a,(ix+E_COMBO)
 inc a
 ld (iy+E_COMBO),a
 ld a,SFX_KICK
 call snd_sfx
 jr .next
.boss:
 ld a,(iy+E_STATE)
 cp S_DYING
 jr z,.next
 ld a,(iy+E_INV)
 or a
 jr nz,.next
 pop bc
 call boss_damage
 jp kill_rolled
.next:
 pop bc
 ld de,ENT_SIZE
 add iy,de
 djnz .l
 ret

; IX = rolling ball that ends: the gassed enemy inside dies
kill_rolled:
 ld a,(ix+E_COMBO)
 inc a
 jp kill_enemy

; IX = enemy to kill, a = combo level (1..)
kill_enemy:
 ld (tmp2),a
 ld (ix+E_STATE),S_DYING
 ld (ix+E_VY),$FD
 ld (ix+E_VYF),$80
 ld (ix+E_TUFO),0
 ld a,(ix+E_X)
 ld (kill_x),a
 ld a,(ix+E_Y)
 ld (kill_y),a
 ; score: base by type, doubled per combo
 ld a,(ix+E_TYPE)
 cp T_BOLA
 ld hl,score_bola
 jr z,.sc
 ld hl,score_escoba
.sc:
 ld a,(tmp2)
 dec a
 cp 5
 jr c,.ci
 ld a,4
.ci:
 add a,a
 ld e,a
 ld d,0
 add hl,de
 ld a,(hl)
 inc hl
 ld c,(hl)
 call add_score
 ld a,SFX_POP
 call snd_sfx
 ld a,(kill_x)
 ld b,a
 ld a,(kill_y)
 ld c,a
 call spawn_stars
 jp drop_item

; BCD scores (low, high) for combo x1..x16
score_bola:   db $40,$00, $80,$00, $60,$01, $20,$03, $40,$06
score_escoba: db $80,$00, $60,$01, $20,$03, $40,$06, $80,$12

st_dying:
 ld l,(ix+E_VYF)
 ld h,(ix+E_VY)
 ld de,$0028
 add hl,de
 ld (ix+E_VYF),l
 ld (ix+E_VY),h
 ld e,(ix+E_YF)
 ld d,(ix+E_Y)
 add hl,de
 ld (ix+E_YF),l
 ld (ix+E_Y),h
 ld a,h
 cp 192
 jr c,.ok
 cp 232
 jr nc,.ok
 ld (ix+E_TYPE),0
 ret
.ok:
 inc (ix+E_ANIM)
 ret

; ---------------------------------------------------------------------
; collision helpers
; overlap_player: IX entity vs player (shrunk boxes) -> carry if overlap
overlap_player:
 ld iy,player
; overlap_iy: IX vs IY (uses E_W/E_H, 3px margins) -> carry if overlap
overlap_iy:
 ; x: ix.x+3 < iy.x+iy.w-3  and  iy.x+3 < ix.x+ix.w-3
 ld a,(iy+E_X)
 add a,(iy+E_W)
 sub 3
 ld c,a
 ld a,(ix+E_X)
 add a,3
 cp c
 jr nc,.no
 ld a,(ix+E_X)
 add a,(ix+E_W)
 sub 3
 ld c,a
 ld a,(iy+E_X)
 add a,3
 cp c
 jr nc,.no
 ld a,(iy+E_Y)
 add a,(iy+E_H)
 sub 3
 ld c,a
 ld a,(ix+E_Y)
 add a,3
 cp c
 jr nc,.no
 ld a,(ix+E_Y)
 add a,(ix+E_H)
 sub 3
 ld c,a
 ld a,(iy+E_Y)
 add a,3
 cp c
 jr nc,.no
 scf
 ret
.no:
 or a
 ret

; harmful enemy touching willow?
touch_player:
 ld a,(ix+E_TUFO)
 or a
 ret nz
 ld a,(ix+E_STATE)
 cp S_NORMAL
 ret nz
touch_always:
 call overlap_player
 ret nc
 jp player_hit

; ---------------------------------------------------------------------
;  LA LAVADORA (boss)
; ---------------------------------------------------------------------
boss_update:
 ld a,(ix+E_STATE)
 cp S_DYING
 jp z,boss_dying
 cp S_APPEAR
 jr nz,.go
 dec (ix+E_TIMER)
 ret nz
 ld (ix+E_STATE),S_NORMAL
 ld (ix+E_TIMER),120
 ret
.go:
 ld a,(ix+E_INV)
 or a
 jr z,.ni
 dec (ix+E_INV)
.ni:
 inc (ix+E_ANIM)
 ; hum
 ld hl,$0080
 ld de,$0020
 call speed_calc
 bit F_GROUND,(ix+E_FLAGS)
 jr nz,.walk
 ld hl,$0100
.walk:
 call set_vx_dir
 ld a,(ix+E_FLAGS)
 ld (tmp1),a
 call ent_physics
 bit F_WALL,(ix+E_FLAGS)
 jr z,.nw
 ld a,(ix+E_DIR)
 xor 1
 ld (ix+E_DIR),a
.nw:
 ; landed this frame after a hop?
 ld a,(tmp1)
 bit F_GROUND,a
 jr nz,.nl
 bit F_GROUND,(ix+E_FLAGS)
 jr z,.nl
 ld a,10
 ld (shake),a
 ld a,SFX_CLANG
 call snd_sfx
 call boss_spit
.nl:
 dec (ix+E_TIMER)
 jr nz,.th
 ld a,(difficulty)
 or a
 ld a,150
 jr z,.t
 ld a,105
.t:
 ld (ix+E_TIMER),a
 bit F_GROUND,(ix+E_FLAGS)
 jr z,.th
 ld (ix+E_VY),$FC
 ld (ix+E_VYF),$80
 ; turn towards willow
 ld a,(player+E_X)
 cp (ix+E_X)
 ld a,0
 jr nc,.d
 inc a
.d:
 ld (ix+E_DIR),a
.th:
 jp touch_always

; spawn a Bola from the drum door
boss_spit:
 ld a,(bolas_alive)
 cp 3
 ret nc
 ld a,(ix+E_X)
 add a,8
 ld d,a
 ld a,(ix+E_Y)
 add a,4
 ld e,a
 push ix
 ld a,T_BOLA
 call spawn_enemy
 jr c,.full
 ld (ix+E_STATE),S_NORMAL
 ld (ix+E_VY),$FC
 ld a,(player+E_X)
 cp d
 ld a,0
 jr nc,.dd
 inc a
.dd:
 ld (ix+E_DIR),a
.full:
 pop ix
 ret

; IY = boss
boss_damage:
 ld (iy+E_INV),40
 ld a,SFX_BOSSHIT
 call snd_sfx
 ld a,$00
 ld c,$01
 call add_score
 ld a,(iy+E_HP)
 dec a
 ld (iy+E_HP),a
 ld (boss_hp),a
 ld hl,hud_dirty
 set 4,(hl)
 or a
 ret nz
 ; defeated!
 ld (iy+E_STATE),S_DYING
 ld (iy+E_TIMER),120
 ld a,1
 ld (boss_dead),a
 ld a,$00
 ld c,$15
 call add_score       ; 1500
 ; every other enemy dies
 push ix
 ld ix,enemies
 ld b,MAX_ENEMY
.k:
 push bc
 ld a,(ix+E_TYPE)
 cp T_BOLA
 jr z,.kk
 cp T_ESCOBA
 jr nz,.kn
.kk:
 ld a,(ix+E_STATE)
 cp S_DYING
 jr z,.kn
 ld a,1
 call kill_enemy
.kn:
 pop bc
 ld de,ENT_SIZE
 add ix,de
 djnz .k
 pop ix
 ret

boss_dying:
 inc (ix+E_ANIM)
 ld a,(ix+E_TIMER)
 and 7
 jr nz,.ns
 ld a,6
 ld (shake),a
 call rand
 and 31
 add a,(ix+E_X)
 ld b,a
 call rand
 and 31
 add a,(ix+E_Y)
 ld c,a
 call spawn_stars
 ld a,SFX_POP
 call snd_sfx
.ns:
 dec (ix+E_TIMER)
 ret nz
 ld (ix+E_TYPE),0
 xor a
 ld (boss_active),a
 ret

; ---------------------------------------------------------------------
;  LA ASPIRADORA (hurry-up)
; ---------------------------------------------------------------------
hurry_update:
 ld a,(clear_timer)
 or a
 ret nz
 ld a,(player+E_STATE)
 cp P_PLAY
 ret nz
 ld a,(hurry_state)
 cp 2
 ret z
 ld hl,(hurry_timer)
 dec hl
 ld (hurry_timer),hl
 ld a,h
 or l
 ret nz
 ld a,(hurry_state)
 or a
 jr nz,.release
 ; warning
 ld a,1
 ld (hurry_state),a
 ld hl,240
 ld (hurry_timer),hl
 ld a,4                ; music speeds up (main theme runs at 5)
 ld (snd_tempo),a
 ld a,SFX_HURRY
 call snd_sfx
 ld hl,txt_hurry
 ld a,200
 jp show_msg
.release:
 ld a,2
 ld (hurry_state),a
 ; enter from the top corner away from willow
 ld a,(player+E_X)
 cp 128
 ld d,224
 jr c,.side
 ld d,16
.side:
 ld e,24
 ld a,T_ASPIRA
 call spawn_enemy
 ret c
 ld (ix+E_STATE),S_NORMAL
 ret

vacuum_update:
 inc (ix+E_ANIM)
 ld a,(player+E_STATE)
 cp P_PLAY
 ret nz
 ; speed: normal moves 3 of 4 frames, hardcore every frame
 ld a,(difficulty)
 or a
 jr nz,.go
 ld a,(frame_cnt)
 and 3
 ret z
.go:
 ld a,(player+E_X)
 cp (ix+E_X)
 jr z,.ydir
 jr c,.left
 inc (ix+E_X)
 ld (ix+E_DIR),0
 jr .ydir
.left:
 dec (ix+E_X)
 ld (ix+E_DIR),1
.ydir:
 ld a,(frame_cnt)
 and 1
 jr z,.t
 ld a,(player+E_Y)
 cp (ix+E_Y)
 jr z,.t
 jr c,.up
 inc (ix+E_Y)
 jr .t
.up:
 dec (ix+E_Y)
.t:
 jp touch_always

kill_vacuum:
 ld ix,enemies
 ld b,MAX_ENEMY
.l:
 ld a,(ix+E_TYPE)
 cp T_ASPIRA
 jr nz,.n
 ld (ix+E_TYPE),0
.n:
 ld de,ENT_SIZE
 add ix,de
 djnz .l
 ld a,6
 ld (snd_tempo),a
 xor a
 ld (hurry_state),a
 ret
