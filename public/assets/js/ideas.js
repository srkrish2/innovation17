(function(global){
	var currentIdea;
	$(document).on('click','.proceed',function(e){
		$('.ui.modal').modal('show');
	});
	$(document).on('click','.startsuggestion',function(e){
		$('.ui.modal').hide();
		var feedbacks = $('.feedback'), feedbackArray = [];
		for (var i = 0; i<feedbacks.length; i++){
			feedbackArray.push(feedbacks[i].val());
		}
		$.ajax({
			type: 'POST',
			url: '/post_feedback',//per idea
			contentType: 'application/json; charset=utf-8',
			data: JSON.stringify({
				'idea_id':currentIdea,//length of class list is 6
				'feedbacks': feedbackArray,
				'count_goal': $('.count_goal').val()
			}),
			success: function(sdata){
				$('tr.'+currentIdea+' td')[4].html('<div class="ui button view"><a href='+ sdata["idea_slug"]+'><i class="icon doctor"></i>0</a></div>');
				console.log('launched suggestion seeking');
				// window.location.replace(sdata['url']);
			},
			error: function(e){
				console.log("error! "+e);
			}
		})
		
	});
	$(document).on('click','.cancelinspiration',function(e){
		$('.ui.modal').modal('hide');
	});
	$(document).on('click','.ui.button.rj', function(e){
		
		if(!$(e.currentTarget.parentElement.parentElement).hasClass('rj')){
			$(e.currentTarget.parentElement.parentElement).addClass('rj');
		}
	});
	$(document).on('click','.ui.button.ac', function(e){
		currentIdea = $(e.currentTarget.parentElement.parentElement).attr('class');
		if($(e.currentTarget.parentElement.parentElement).hasClass('rj')){
			$(e.currentTarget.parentElement.parentElement).removeClass('rj');
		}
	});
	$(document).on('click','.addfeedback', function(e){
		$('<div class="field"><input type="text" class="feedback" placeholder="Enter the feedback for the idea">').insertBefore($(e.currentTarget));
	});
	$(document).on('click','.ui.button.view', function(e){
		$('<div class="field"><input type="text" class="feedback" placeholder="Enter the feedback for the idea">').insertBefore($(e.currentTarget));
	});
}(window));