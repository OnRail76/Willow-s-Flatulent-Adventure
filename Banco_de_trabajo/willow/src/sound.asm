; =====================================================================
;  sound.asm - PSG music + SFX driver (runs in the frame interrupt)
; =====================================================================
; channel struct (16 bytes) at snd_ch + n*16, n = 0..2 tone, 3 = drums
CH_PTR      equ 0
CH_START    equ 2
CH_DUR      equ 4
CH_VOL      equ 5
CH_ENV      equ 6
CH_ATT      equ 7
CH_PER      equ 8
CH_MEOWF    equ 10
CH_MEOWT    equ 11
CH_ENVT     equ 12
CH_ON       equ 13
CH_NUM      equ 14

snd_init:
 xor a
 ld (snd_mus_on),a
 ld hl,0
 ld (snd_sfx_ptr),hl
 ld a,6
 ld (snd_tempo),a
snd_silence:
 ld a,$9F
 out (PSG_PORT),a
 ld a,$BF
 out (PSG_PORT),a
 ld a,$DF
 out (PSG_PORT),a
 ld a,$FF
 out (PSG_PORT),a
 ret

; a = song number
snd_play_music:
 ld c,a
 ld a,i               ; P/V = IFF2
 push af
 di
 ld a,c
 ld (snd_cur_song),a
 add a,a
 ld e,a
 ld d,0
 ld hl,song_table
 add hl,de
 ld e,(hl)
 inc hl
 ld d,(hl)            ; de -> song header (4 dw)
 ld ix,snd_ch
 ld b,4
 ld c,0
.ch:
 ld a,(de)
 ld (ix+CH_PTR),a
 ld (ix+CH_START),a
 inc de
 ld a,(de)
 ld (ix+CH_PTR+1),a
 ld (ix+CH_START+1),a
 inc de
 ld (ix+CH_DUR),1
 ld (ix+CH_ATT),15
 ld (ix+CH_ON),1
 ld (ix+CH_NUM),c
 ld (ix+CH_MEOWF),0
 ld (ix+CH_MEOWT),0
 ld (ix+CH_VOL),2
 ld (ix+CH_ENV),1
 push de
 ld de,16
 add ix,de
 pop de
 inc c
 djnz .ch
 ld a,1
 ld (snd_mus_on),a
 ld (snd_tick),a
 ld a,(snd_cur_song)
 ld e,a
 ld d,0
 ld hl,song_tempo
 add hl,de
 ld a,(hl)
 ld (snd_tempo),a
 pop af
 ret po
 ei
 ret

snd_stop_music:
 xor a
 ld (snd_mus_on),a
 jp snd_silence

; a = sfx number (1..)
snd_sfx:
 push hl
 push de
 dec a
 add a,a
 ld e,a
 ld d,0
 ld hl,sfx_table
 add hl,de
 ld e,(hl)
 inc hl
 ld d,(hl)
 ld a,i
 di
 ld (snd_sfx_ptr),de
 jp po,.noei
 ei
.noei:
 pop de
 pop hl
 ret

; ---------------------------------------------------------------------
snd_update:
 ld a,(snd_mus_on)
 or a
 jr z,.nomus
 ld hl,snd_tick
 dec (hl)
 jr nz,.noread
 ld a,(snd_tempo)
 ld (hl),a
 ld ix,snd_ch
 call ch_tick
 ld ix,snd_ch+16
 call ch_tick
 ld ix,snd_ch+32
 call ch_tick
 ld ix,snd_ch+48
 call drum_tick
.noread:
 ld hl,(snd_sfx_ptr)
 ld a,h
 or l
 jr z,.dk0
 ld a,6
.dk0:
 ld (snd_duck),a
 ld ix,snd_ch
 call ch_frame
 ld ix,snd_ch+16
 call ch_frame
 ld hl,(snd_sfx_ptr)
 ld a,h
 or l
 jr nz,.nomus          ; sfx owns channel 2 + noise
 ld ix,snd_ch+32
 call ch_frame
 call drum_frame
.nomus:
 ; ---- sfx ----
 ld hl,(snd_sfx_ptr)
 ld a,h
 or l
 ret z
 ld e,(hl)
 inc hl
 ld d,(hl)
 inc hl
 ld a,d
 cp $FF
 jr z,.sfxend
 ; tone 2 period
 ld a,e
 and 15
 or $C0
 out (PSG_PORT),a
 ld a,e
 srl d
 rra
 srl d
 rra
 srl d
 rra
 srl d
 rra
 and $3F
 out (PSG_PORT),a
 ld a,(hl)
 inc hl
 and 15
 or $D0
 out (PSG_PORT),a
 ld a,(hl)
 inc hl
 cp $FF
 jr z,.nonctl
 and 7
 or $E0
 out (PSG_PORT),a
.nonctl:
 ld a,(hl)
 inc hl
 and 15
 or $F0
 out (PSG_PORT),a
 ld (snd_sfx_ptr),hl
 ret
.sfxend:
 ld hl,0
 ld (snd_sfx_ptr),hl
 ld a,$DF
 out (PSG_PORT),a
 ld a,$FF
 out (PSG_PORT),a
 ld a,(snd_mus_on)
 or a
 ret z
 ; force channel 2 period rewrite next frame
 ld ix,snd_ch+32
 ret

; --- read events for a tone channel at tick boundary ---
ch_tick:
 ld a,(ix+CH_ON)
 or a
 ret z
 dec (ix+CH_DUR)
 ret nz
 ld l,(ix+CH_PTR)
 ld h,(ix+CH_PTR+1)
.ev:
 ld a,(hl)
 inc hl
 cp $F0
 jr c,.note
 cp $FF
 jr z,.loop
 cp $FE
 jr z,.end
 cp $F0
 jr z,.vol
 cp $F1
 jr z,.env
 ; $F2 meow
 ld (ix+CH_MEOWF),1
 jr .ev
.vol:
 ld a,(hl)
 inc hl
 ld (ix+CH_VOL),a
 jr .ev
.env:
 ld a,(hl)
 inc hl
 ld (ix+CH_ENV),a
 jr .ev
.loop:
 ld l,(ix+CH_START)
 ld h,(ix+CH_START+1)
 jr .ev
.end:
 ld (ix+CH_ON),0
 ld (ix+CH_ATT),15
 dec hl
 ld (ix+CH_PTR),l
 ld (ix+CH_PTR+1),h
 ld a,(ix+CH_NUM)
 jp ch_mute
.note:
 ld b,a               ; note index (0 = rest)
 ld a,(hl)
 inc hl
 ld (ix+CH_DUR),a
 ld (ix+CH_PTR),l
 ld (ix+CH_PTR+1),h
 ld a,b
 or a
 jr z,.rest
 add a,a
 ld e,a
 ld d,0
 ld hl,note_periods
 add hl,de
 ld a,(hl)
 ld (ix+CH_PER),a
 inc hl
 ld a,(hl)
 ld (ix+CH_PER+1),a
 ld a,(ix+CH_VOL)
 ld (ix+CH_ATT),a
 ld (ix+CH_ENVT),0
 ld a,(ix+CH_MEOWF)
 ld (ix+CH_MEOWT),a
 ld (ix+CH_MEOWF),0
 ret
.rest:
 ld (ix+CH_ATT),15
 ld (ix+CH_MEOWF),0
 ld (ix+CH_MEOWT),0
 ret

; a = channel (0..2): silence
ch_mute:
 rrca
 rrca
 rrca
 or $9F
 out (PSG_PORT),a
 ret

; --- per-frame output for a tone channel ---
ch_frame:
 ld a,(ix+CH_ON)
 or a
 ret z
 ; envelope
 inc (ix+CH_ENVT)
 ld a,(ix+CH_ENV)
 or a
 jr z,.envdone
 ld b,7               ; slow decay: every 8 frames
 cp 1
 jr z,.e1
 ld b,1               ; staccato: every 2 frames
.e1:
 ld a,(ix+CH_ENVT)
 and b
 jr nz,.envdone
 ld a,(ix+CH_ATT)
 cp 15
 jr z,.envdone
 ; slow decay stops at vol+5
 ld c,a
 ld a,(ix+CH_ENV)
 cp 1
 ld a,c
 jr nz,.inc
 ld a,(ix+CH_VOL)
 add a,5
 cp c
 jr z,.envdone
 jr c,.envdone
.inc:
 inc (ix+CH_ATT)
.envdone:
 ; period (+ meow bend)
 ld l,(ix+CH_PER)
 ld h,(ix+CH_PER+1)
 ld a,(ix+CH_MEOWT)
 or a
 jr z,.noMeow
 cp 24
 jr nc,.mhold
 inc (ix+CH_MEOWT)
.mhold:
 dec a
 cp 23
 jr c,.mi
 ld a,23
.mi:
 ld e,a
 ld d,0
 push hl
 ld hl,meow_tab
 add hl,de
 ld a,(hl)            ; signed multiplier
 pop hl
 push hl
 ; de = period >> 4
 srl h
 rr l
 srl h
 rr l
 srl h
 rr l
 srl h
 rr l
 ex de,hl
 pop hl
 or a
 jr z,.noMeow
 bit 7,a
 jr nz,.neg
.padd:
 add hl,de
 dec a
 jr nz,.padd
 jr .noMeow
.neg:
 or a
 sbc hl,de
 inc a
 jr nz,.neg
.noMeow:
 ; write period: latch $80 | ch<<5 | low nibble
 ld a,(ix+CH_NUM)
 rrca
 rrca
 rrca
 ld c,a               ; ch<<5
 ld a,l
 and 15
 or c
 or $80
 out (PSG_PORT),a
 ld a,l
 srl h
 rra
 srl h
 rra
 srl h
 rra
 srl h
 rra
 and $3F
 out (PSG_PORT),a
 ld a,(snd_duck)          ; music ducks under sound effects
 add a,(ix+CH_ATT)
 cp 16
 jr c,.nodk
 ld a,15
.nodk:
 or c
 or $90
 out (PSG_PORT),a
 ret

meow_tab:
 db 4,3,2,1,0,-1,-1,-1,-1,0,0,1,1,2,2,3,3,4,4,5,5,6,6,6

; --- drums ---
drum_tick:
 ld a,(ix+CH_ON)
 or a
 ret z
 dec (ix+CH_DUR)
 ret nz
 ld l,(ix+CH_PTR)
 ld h,(ix+CH_PTR+1)
.ev:
 ld a,(hl)
 inc hl
 cp $FF
 jr nz,.n1
 ld l,(ix+CH_START)
 ld h,(ix+CH_START+1)
 jr .ev
.n1:
 cp $FE
 jr nz,.n2
 ld (ix+CH_ON),0
 ld (ix+CH_ATT),15
 ret
.n2:
 ld b,a
 ld a,(hl)
 inc hl
 ld (ix+CH_DUR),a
 ld (ix+CH_PTR),l
 ld (ix+CH_PTR+1),h
 ld a,b
 or a
 ret z
 ; drum b: set noise ctl + start att + decay speed
 dec a
 add a,a
 add a,a
 ld e,a
 ld d,0
 ld hl,drum_defs
 add hl,de
 ld a,(hl)
 ld (ix+CH_PER),a     ; noise ctl
 inc hl
 ld a,(hl)
 ld (ix+CH_ATT),a
 inc hl
 ld a,(hl)
 ld (ix+CH_ENV),a     ; decay step per frame
 ld (ix+CH_MEOWT),1   ; "new hit" flag -> write ctl
 ret
drum_defs:      ; ctl, start att, decay
 db 2,3,3,0     ; kick: periodic low thump
 db 5,5,2,0     ; snare
 db 4,10,3,0    ; hat
 db 4,4,1,0     ; crash

drum_frame:
 ld ix,snd_ch+48
 ld a,(ix+CH_ON)
 or a
 ret z
 ld a,(ix+CH_MEOWT)
 or a
 jr z,.nohit
 ld (ix+CH_MEOWT),0
 ld a,(ix+CH_PER)
 or $E0
 out (PSG_PORT),a
.nohit:
 ld a,(ix+CH_ATT)
 cp 15
 jr nc,.out
 add a,(ix+CH_ENV)
 cp 15
 jr c,.ok
 ld a,15
.ok:
 ld (ix+CH_ATT),a
.out:
 ld a,(ix+CH_ATT)
 or $F0
 out (PSG_PORT),a
 ret
