(function(global){
	$(document).on('click','.proceed',function(e){
		$('.ui.modal').modal('show');
	});
	$(document).on('click','.startinspiration',function(e){
		$('.ui.modal').hide();
		var acceptedschemas = $('.ui.button.ac').parents('td.action');
		$(e.currentTarget).prop('disabled',true);
		$.ajax({
			type: 'POST',
			url: '/post_inspiration_task',
			contentType: 'application/json; charset=utf-8',
			data: JSON.stringify({
				'problem_id':$('thead').attr('class'),//length of class list is 6
				'count_goal': $('.count_goal').val()
			}),
			success: function(sdata){
		// 		for (var i =0; i<acceptedschemas.length; i++){ if after launching we need to come back to schema list page, implement this, otherwise delete
			
		// }
		console.log('launched inspiration');
		window.location.replace('/problems');
		$(e.currentTarget).prop('disabled',false);
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
	$(document).on('click','.ui.button.rj, .ui.button.ac, .reactivate',function(e){
		e.preventDefault();
		$(e.currentTarget).prop('disabled',true);
		var itemType = "schema", toreject=$(e.currentTarget).hasClass('red'), item_id = $(e.currentTarget.parentElement.parentElement.parentElement).attr('class').split('-')[2];//if red exist, that means currently is accepted, now being hit-> changing to rej

		$.ajax({
			type: 'POST',
			url: '/post_reject',
			contentType: 'application/json; charset=utf-8',
			data: JSON.stringify({
				"to_reject": toreject,
				"type": itemType,
				"id": item_id.split(' ')[0]
			}),
			
			success: function(sdata){
				$(e.currentTarget).prop('disabled',false);
				if($(e.currentTarget).hasClass('reactivate')){
					$(e.currentTarget).html('Activated into accepted');
				}
				else {
					if(toreject){
						$(e.currentTarget).addClass('active');
						$(e.currentTarget).siblings().removeClass('active');
						$(e.currentTarget.parentElement.parentElement.parentElement).addClass('rj');
					}
				else {//accept it, next available action is reject
					$(e.currentTarget).addClass('active');
					$(e.currentTarget).siblings().removeClass('active');
					$(e.currentTarget.parentElement.parentElement.parentElement).removeClass('rj');
				}
			}
			console.log('rejected schema id '+item_id);
		},
		error: function(e){
			console.log('error! ' + e);
		}
	});
	});
}(window));