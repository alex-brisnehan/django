#encoding: UTF-8
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors 
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm

from django.http import HttpResponse
from django.utils.html import escape

from dj_pro import models

def album_pdf(request, id):
    """
    Produces a printable PDF of the album sutable for slipping in a CD case.
    """
    
    obj = models.Album.objects.get(pk=id)

    styles = {'normal': ParagraphStyle(name='normal', fontName='Times-Roman', fontSize=0.5*cm, leading=0.45*cm),
              'small': ParagraphStyle(name='small', fontName='Times-Roman', fontSize=0.3*cm, leading=0.29*cm),
              'review': ParagraphStyle(name='review', fontName='Times-Roman', fontSize=10, leading=10.2),
              'song': ParagraphStyle(name='song', fontName='Times-Roman', fontSize=0.4*cm, alignment=1),
              'location': ParagraphStyle(name='location', fontName="Helvetica-Bold", fontSize=0.4*cm)}
    
    # Build the artist/album header
    art_alb_style=[('BACKGROUND', (0,0), (-1,0), colors.black),
                   ('TEXTCOLOR', (0,0), (-1,0), colors.white), 
                   ('LEFTPADDING', (0,0), (-1,0), 0.4*cm),
                   ('FONT', (0,0), (-1,0), 'Helvetica', 0.3*cm),
                   ('LEFTPADDING', (0,1), (-1,1), 0.2*cm),
                   ('RIGHTPADDING', (0,1), (-1,1), 1),
                   ('TOPPADDING', (0,0), (-1,-1), -0.27*cm),
                   ('BOTTOMPADDING', (0,0), (-1,-1), 0),
                   ('LINEAFTER', (0,1), (0,1), 0.3, colors.black),
                   ('VALIGN', (0,1), (-1,-1), 'MIDDLE')]
    
    album = Paragraph(escape(obj.album), styles['normal'])
    if obj.artist:
        artist = Paragraph(escape(obj.artist.artist), styles['normal'])
        
        # Change the style and spacing if they're too big
        artist.wrap(5.8*cm, 1*cm)
        if artist.minWidth() > 5.8*cm or len(artist.getActualLineWidths0()) > 2:
            artist = Paragraph(artist.text, styles['small'])
            art_alb_style.append(('TOPPADDING', (0,1), (0,1), -0.1*cm))
        
        album.wrap(5.8*cm, 1*cm)
        if album.minWidth() > 5.8*cm or len(album.getActualLineWidths0()) > 2:
            album = Paragraph(album.text, styles['small'])
            art_alb_style.append(('TOPPADDING', (1,1), (1,1), -0.1*cm))
        
        artist_album = Table([[u'Artist', u'Album'], [artist, album]],
            colWidths = [6*cm, 6*cm],
            rowHeights = [0.3*cm, 1.3*cm],
            style = art_alb_style)

    else:
        #compilation
        artist_album = Table([[u'Album'], [album]],
            colWidths = [12*cm],
            rowHeights = [0.3*cm, 1.3*cm],
            style = art_alb_style)

    
    # Build the song section
    song_style = [('TOPPADDING', (0,0), (-1,-1), -2),
                  ('BOTTOMPADDING', (0,0), (-1,-1), 0),
                  ('LEFTPADDING', (0,0), (-1,-1), 0),
                  ('RIGHTPADDING', (0,0), (-1,-1), 0),
                  ('BACKGROUND', (0,0), (-1,0), colors.black),
                  ('TEXTCOLOR', (0,0), (-1,0), colors.white), 
                  ('FONT', (0,0), (-1,0), 'Helvetica', 0.31*cm),
                  ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                  ('LEFTPADDING', (1,0), (1,0), 0.4*cm),
                  ('ALIGN', (1,0), (1,-1), 'LEFT'),
                  ('INNERGRID', (0,1), (-1,-1), 0.3, colors.black),
                  ('LINEBELOW', (0,-1), (-1,-1), 0.3, colors.black),
                  ('VALIGN', (0,1), (-1,-1), 'MIDDLE'),
                  ('TOPPADDING', (1,1), (1,-1), -1),
                  ('BOTTOMPADDING', (1,1), (1,-1), 0.2*cm),
                  ('LEFTPADDING', (1,1), (1,-1), 0.1*cm)]
    
    song_data = [[u'#', u'Song Title', u'In', u'Tempo', u'Time', u'End']]

    good_songs = obj.song_set.filter(rating__gt=3).order_by('-rating')
    for i in range(0, 5):
        if i >= len(good_songs):
            song_data.append(['', '', '', '', '', ''])
            continue
        
        if good_songs[i].comp_artist:
            song_name = u'%s — %s' % (good_songs[i].song, good_songs[i].artist.artist)
        else:
            song_name = good_songs[i].song
        song_name = Paragraph(escape(song_name), styles['normal'])
        song_name.wrap(6.1*cm, cm)
        if len(song_name.getActualLineWidths0()) > 1:
            song_name = Paragraph(song_name.text, styles['small'])
            song_style.append(('BOTTOMPADDING', (1, i+1), (1, i+1), 2))
        
        if good_songs[i].rating > 4:
            track = u'<b><u>%s</u></b>' % escape(good_songs[i].track)
        else:
            track = escape(good_songs[i].track)
        
        song_data.append([Paragraph(track, styles['song']),
            song_name,
            Paragraph(escape(good_songs[i].ramp), styles['song']),
            Paragraph(escape(good_songs[i].tempo), styles['song']),
            Paragraph(escape(good_songs[i].length), styles['song']),
            Paragraph(escape(good_songs[i].post), styles['song'])])
    
    songs = Table(song_data,
        colWidths = [0.9*cm, 6.2*cm, 1.2*cm, 1.2*cm, 1.3*cm, 1.2*cm],
        style = song_style)
    
    # build the review
    review = Paragraph(escape(obj.review), styles['review'])
    
    # build the other track listing
    other_style = [('TOPPADDING', (0,0), (0,-1), 0),
                   ('BOTTOMPADDING', (0,0), (0,-1), 0),
                   ('BACKGROUND', (0,0), (0,-1), colors.black),
                   ('TEXTCOLOR', (0,0), (0,-1), colors.white), 
                   ('RIGHTPADDING', (0,0), (0,-1), 0.2*cm),
                   ('FONT', (0,0), (0,-1), 'Helvetica-Bold', 0.3*cm),
                   ('ALIGN', (0,0), (0,-1), 'RIGHT'),
                   ('LINEABOVE', (1,0), (1,1), 0.3, colors.black),
                   ('LINEABOVE', (0,0), (0,0), 0.3, colors.black),
                   ('VALIGN', (1,0), (1,1), 'TOP'),
                   ('TOPPADDING', (1,0), (1,-1), -1.5)
    ]
    
    also_play = list(obj.song_set.filter(rating__gt=1, rating__lt=4)) + good_songs[5:]
    also_play = u', '.join([((u'<b><u>%s</u></b>' % x.track) if x.rating > 2 else x.track) for x in also_play])
    also_play = Paragraph(also_play, styles['review'])
    do_not_play = u', '.join(obj.song_set.filter(rating=0).values_list('track', flat=True))
    do_not_play = Paragraph(do_not_play, styles['review'])
    
    other_tracks = Table( [[u'Also recommended:', also_play],
                           [u'DO NOT PLAY:', do_not_play]],
        colWidths = [4*cm, 8*cm],
        rowHeights = [0.35*cm, 0.35*cm],
        style = other_style)
    
    #Put them all together
    final_style = [('BOX', (0,0), (-1,-1), 1, colors.black),
                   ('LEFTPADDING', (0,0), (-1,-1), 0),
                   ('TOPPADDING', (0,0), (-1,-1), 0),
                   ('RIGHTPADDING', (0,0), (-1,-1), 0),
                   ('BOTTOMPADDING', (0,0), (-1,-1), 0),
                   ('VALIGN', (0,0), (0,2), 'TOP'),
                   ('RIGHTPADDING', (0,2), (0,2), 0.1*cm),
                   ('LEFTPADDING', (0,2), (0,2), 0.2*cm)]
                   
    elems = []    
    elems.append(
        Table([[artist_album], [songs], [review], [other_tracks]],
            colWidths=[12*cm],
            rowHeights=[1.6*cm, 3.9*cm, 5.8*cm, 0.7*cm],
            style=final_style)
        )
    
    # For the CD location on the edge
    elems.append(Paragraph(escape(obj.location), styles['location']))
    
    response = HttpResponse(mimetype='application/pdf')
    doc = SimpleDocTemplate(response, pagesize=letter, title=u"Insert for the CD")
    doc.build(elems)
    return response
    
