var socket = io();

socket.on('connect', () => {
  console.log(socket.connected); // true
});

socket.emit('mensaje', 'empezar');

socket.on('mensaje', function(msj){
    $('<div class="bot"><p>' + msj + '</p></div>').appendTo($('.historial'));
    console.log(msj);
    $(".historial").animate({ scrollTop: $('.historial')[0].scrollHeight}, 1000);
});

function envio(){
    if ($('.msjentrada').val() == '') {
        alert("Escribe algo")
      }else {
        socket.emit('mensaje', $('.msjentrada').val());
        console.log($('.msjentrada').val());
        $('<div class="usuario"><p>' + $('.msjentrada').val() + '</p></div>').appendTo($('.historial'));
        $('.msjentrada').val('');
        $(".historial").animate({ scrollTop: $('.historial')[0].scrollHeight}, 1000);
    }
}


$('.msjentrada').on('keydown', function(e) {
  if (e.which == 13) {
      envio();
  }
})
