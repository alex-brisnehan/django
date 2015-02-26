-- Remember to change the client encoding to WIN1252

INSERT INTO dj_pro_artist (id, artist, search, sort, last_played, times_played, info, url) 
SELECT artistid, name, lower(name), lower(name), lastplayed, timesplayed, COALESCE(info,''), COALESCE(url,'') 
FROM artist;

SELECT setval('dj_pro_artist_id_seq', MAX(id)) FROM dj_pro_artist;

INSERT INTO dj_pro_album ( id, album, search, sort, artist_id, label, review, year, location, added_on)
SELECT cdid, title, lower(title), lower(title), artistid, label, COALESCE(review, ''), year, location, dateadded 
FROM cd;

SELECT setval('dj_pro_album_id_seq', MAX(id)) FROM dj_pro_album;

INSERT INTO dj_pro_rotation (id, rotation, max)
SELECT rotationid, rotation, COALESCE(maxcount, 0)
FROM rotation;

SELECT setval('dj_pro_rotation_id_seq', MAX(id)) FROM dj_pro_rotation;

INSERT INTO dj_pro_song 
  (id, song, search, album_id, comp_artist_id, artist_id, length, last_played, times_played, track, tempo, ramp, post, rating, rotation_id, added_on) 
SELECT songid, name, lower(name), cdid, artistid, effartistid, to_char(length, 'MI:SS'), lastplayed, timesplayed, track, tempo, songin, songout, 1, rotationid, added
FROM song;

SELECT setval('dj_pro_song_id_seq', MAX(id)) FROM dj_pro_song;

UPDATE dj_pro_song
SET rating = -2
WHERE song ilike '%*dj pick%';

UPDATE dj_pro_song
SET rating = 0
WHERE song like '*%' AND rating > 0;

INSERT INTO dj_pro_venue (id, venue, sort, location, default_minimum_age, default_time, homepage)
SELECT venueid, venue, lower(venue), '', COALESCE(defaultage, ''), defaulttime, COALESCE(url, '')
FROM venue;

SELECT setval('dj_pro_venue_id_seq', MAX(id)) FROM dj_pro_venue;

INSERT INTO dj_pro_concert (id, venue_id, date, time, we_present, minimum_age, info, site)
SELECT concertid, venueid, date, time, presents, COALESCE(age, ''), COALESCE(info, ''), COALESCE(url, '') 
FROM concert;

SELECT setval('dj_pro_concert_id_seq', MAX(id)) FROM dj_pro_concert;

INSERT INTO dj_pro_performer (concert_id, "order", performer)
SELECT concertid, 30, other
FROM concert
WHERE other IS NOT NULL;

INSERT INTO dj_pro_performer (concert_id, "order", performer, artist_id)
SELECT  concertid, sort, name, concertband.artistid
FROM concertband JOIN artist USING (artistid);


INSERT INTO on_air_playhistory (song_id, played_at)
SELECT songid, timeplayed
FROM pastplayed;

CREATE TEMP sequence temp_seq;
INSERT INTO on_air_rotationschedule ("order", rotation_id)
SELECT nextval('temp_seq') As row_number, rotationid
FROM schedule
ORDER BY time;
DROP SEQUENCE temp_seq;

INSERT INTO on_air_top10 (week_ending)
SELECT DISTINCT "week"
FROM topplayed;

INSERT INTO on_air_top10album (week_id, rank, album_id)
SELECT on_air_top10.id, list, cdid
FROM topplayed JOIN on_air_top10 ON (topplayed.week = on_air_top10.week_ending);


-- Take the pg_authid and rename it to old_auth for this to work.
INSERT INTO auth_user (username, first_name, last_name, email, password, is_staff, is_active, is_superuser, last_login, date_joined) 
SELECT usename, split_part(realname, ' ', 1), regexp_replace(realname, '^[^ ]+ ', ''), COALESCE(email, ''), 'md5$'||usename||'$'||substring(rolpassword from 4), rolsuper, true, rolsuper, last_login, first_login
FROM (dj JOIN pg_authid on (dj.usename = pg_authid.rolname)) JOIN
   (SELECT MAX(login) AS last_login, MIN(login) AS
first_login, username FROM log group by username) as log 
ON (log.username = dj.usename);

INSERT INTO dj_pro_userprofile (user_id, alias, phone)
SELECT auth_user.id, alias, phone
FROM dj JOIN auth_user ON (dj.usename = auth_user.username);

