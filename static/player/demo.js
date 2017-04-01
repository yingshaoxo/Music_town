var ap1 = new APlayer({
    element: document.getElementById('player1'),
    narrow: false,
    autoplay: false,
    showlrc: false,
    mutex: true,
    theme: '#ff6600',
    music: {
            title: 'Playing Love',
            author: '1900',
            url: 'music/Playing Love.mp3',
            pic: 'music/picture/Playing Love.jpg'
        }
    
});
ap1.init();
