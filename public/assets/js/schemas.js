(function(global){
	$(document).on('click','.proceed',function(e){
		$('.ui.modal').show();
	});
	$(document).on('click','.startinspiration',function(e){
		$('.ui.modal').hide();
		$.ajax({
			type: 'POST',
			data: {
				'problem_id':$('table'.attr('class').split()[-1])
			},
			success: function(sdata){
				console.log('launched inspiration');
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