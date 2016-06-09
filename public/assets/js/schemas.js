(function(global){
	$(document).on('click','.proceed',function(e){
		$('.ui.modal').modal('show');
	});
	$(document).on('click','.startinspiration',function(e){
		$('.ui.modal').hide();
		$.ajax({
			type: 'POST',
			url: '/post_inspiration_task',
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
	//reject or accept schema items
	$(document).on('click','.ui.button.rj',function(e){
		var itemType = "schema", toreject=$(e.currentTarget).hasClass('red'), item_id = $(e.currentTarget.parentElement.parentElement).attr('class').split('-')[2];//if red exist, that means currently is accepted, now being hit-> changing to rej

		$.ajax({
			type: 'POST',
			url: '/post_reject',
			contentType: 'application/json; charset=utf-8',
			data: JSON.stringify({
				"to_reject": toreject,
				"type": itemType,
				"id": item_id
			}),
			
			success: function(sdata){
				if(toreject){
					$(e.currentTarget).removeClass('red');
					$(e.currentTarget).html('Accept');
					$(e.currentTarget.parentElement.parentElement).addClass('rj');
				}
				else {
					$(e.currentTarget).addClass('red');
					$(e.currentTarget).html('Reject');
					$(e.currentTarget.parentElement.parentElement).removeClass('rj');
				}
				console.log('rejected schema id '+item_id);
			},
			error: function(e){
				console.log('error! ' + e);
			}
		});
	});
}(window));