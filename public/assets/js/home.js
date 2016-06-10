(function(global) {
	$('.sidebar-context .home.sidebar')
  .sidebar({
    context: $('.sidebar-context')
  });
  // .sidebar('attach events', '.sidebar-context .menu .item');
  console.log("run home.js");
  $(document).on('click', 'i.delete', function(e){
        console.log(e);
        $(this).parent().remove();
    });
  $("<i class='plus icon addproject'></i>").appendTo($('#new_project'));
  // $(document).on('click','i.addproject', function(e){
  //   console.log('click plus icon');
  //   window.location.href="localhost:8080/new_project.html";
  //   global.location.replace = "localhost:8080/new_project.html";
  //   console.log(window.location.href);
  // })
}(window));


// Pls don't remove
//$.ajax({
//    type: 'POST',
//    url: '/test',
//    error: function(e){
//        console.log("error! "+e)
//    }
//})
//window.alert("hi")