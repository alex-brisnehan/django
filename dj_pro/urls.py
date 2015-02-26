from django.conf.urls.defaults import *
from django.contrib.auth import views as auth

urlpatterns = patterns( 'dj_pro.views',
    (r'^$', 'front'),
    (r'^logout/$', auth.logout, {'next_page':'/djpro/'}),
    (r'^search/$', 'search'),
    (r'^profile/$', 'edit_profile'),
    
    (r'^artist/(?P<id>\d+)/$', 'artist_view'),
    (r'^artist/(?P<id>\d+)/edit/$', 'artist_edit'),
    (r'^artist/new/$', 'artist_new'),
    (r'^album/(?P<id>\d+)/$', 'album_view'),
    (r'^album/(?P<id>\d+)/edit/$', 'album_edit'),
    url(r'^album/new/$', 'album_new'),
    
    (r'^album/add_song/$', 'add_song'),
    
    (r'^concerts/$', 'concert_list'),
    (r'^concerts/(?P<id>\d+)/edit/$', 'concert_edit'),
    (r'^concerts/new/$', 'concert_new'),
    (r'^concerts/delete/$', 'concert_delete'),
    
    (r'^genres/$', 'genre_list'),
    (r'^genre/(?P<genre>[^/]+)/$', 'genre'),
    
)

urlpatterns += patterns ('',
    (r'^album/(?P<id>\d+)/print/$', 'dj_pro.print_album.album_pdf'),
)

urlpatterns += patterns ('dj_pro.ajax',
    (r'^artist-list/$', 'artist_list'), 
    (r'^album-list/$', 'album_list'),
    (r'^genre-list/$', 'genre_list'),
)
