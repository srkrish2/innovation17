(function(global) {
	$('.sidebar-context .home.sidebar')
  .sidebar({
    context: $('.sidebar-context')
  })
  .sidebar('attach events', '.sidebar-context .menu .item');
  console.log("run home.js");
  $(document).on('click', 'i.delete', function(e){
        console.log(e);
        $(this).parent().remove();
    });
}(window));