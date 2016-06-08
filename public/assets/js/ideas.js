(function(global){
	$(document).on('click','.proceed',function(e){
		$('.ui.modal').modal('show');
	});
	$(document).on('click','.startidea',function(e){
		$('.ui.modal').hide();
		$.ajax({
			type: 'POST',
			url: '/post_end_task',
			contentType: 'application/json; charset=utf-8',
			data: JSON.stringify({
				'problem_id':$('thead').attr('class'),//length of class list is 6
				'count_goal': $('.count_goal').val()
			}),
			success: function(sdata){
				console.log('launched inspiration');
				window.location.replace('/problems');
			},
			error: function(e){
				console.log("error! "+e);
			}
		})
		
	});
	$(document).on('click','.cancelinspiration',function(e){
		$('.ui.modal').modal('hide');
	});
}(window));