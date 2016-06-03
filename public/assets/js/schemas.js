(function(global){
	$(document).on('click','.proceed',function(e){
		$('.ui.modal').modal('show');
	});
	$(document).on('click','.startinspiration',function(e){
		$('.ui.modal').hide();
		$.ajax({
			type: 'POST',
			url: '/post_inspiration_task',
			data: {
				'problem_id':$('thead').attr('class').split()[5],//length of class list is 6
				'count_goal': $('.count_goal').val()
			},
			success: function(sdata){
				console.log('launched inspiration');
			},
			error: function(e){
				console.log("error! "+e);
			}
		})
		window.location.replace('/problems');
	});
	$(document).on('click','.cancelinspiration',function(e){
		$('.ui.modal').modal('hide');
	});
}(window));