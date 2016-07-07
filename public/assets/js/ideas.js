(function(global){
	//if($('.suggestion-list').length) makePostRequest();
	//var interval = setInterval(makePostRequest,10000);
	var currentIdea, currentTotal;
	$(document).on('click','.proceed',function(e){
		$('.ui.modal.launchnext .teal.ui.label').html($(e.currentTarget.parentElement).siblings()[0].innerHTML);
		$('.ui.modal.launchnext').modal('show');
	});
	$(document).on('click','.startsuggestion',function(e){
		$('.ui.modal').modal('hide');
		var feedbacks = $('input.feedback'), feedbackArray = [];
		for (var i = 0; i<feedbacks.length; i++){
			if(feedbacks[i].value.length)feedbackArray.push(feedbacks[i].value);
		}
		$(e.currentTarget).prop('disabled',true);
		$.ajax({
			type: 'POST',
			url: '/post_feedback',//per idea
			contentType: 'application/json; charset=utf-8',
			data: JSON.stringify({
				'idea_id':currentIdea,//length of class list is 6
				'count_goal': $('.count_goal').val(),
				'feedbacks': feedbackArray
			}),
			success: function(sdata){
				$('tr.'+currentIdea+' td')[3].innerHTML = '<div class="ui button view"><a href="#" class="ui label feedback-list count"><i class="icon doctor"></i>'+(feedbackArray.length+currentTotal)+'</a></div>';
				console.log('launched suggestion seeking');
				$('.ui.modal.launchnext').modal('hide');
				$(e.currentTarget).prop('disabled',false);
				$(':input').val('');
				// makePostRequest();
			},
			error: function(e){
				console.log("error! "+e);
			}
		})
		
	});
	$(document).on('click','.cancelsuggestion',function(e){
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
		currentIdea = $(e.currentTarget.parentElement.parentElement).attr('class');
		e.preventDefault();
		$.ajax({
			type: "POST",
			url: '/get_feedbacks',
			contentType: 'application/json',
			data: JSON.stringify({'idea_id':$(e.currentTarget.parentElement.parentElement).attr('class')}),
			success: function(sdata){
				sdata = sdata['feedbacks'];
				currentTotal = sdata.length;
				$('.ui.modal.display .teal.ui.label').html($(e.currentTarget.parentElement).siblings()[0].innerHTML);
				$('.field.feedback-list').html('');
				for (var i = 0; i < sdata.length; i++){
					$('<div class="feedback item "'+sdata[i]['feedback_id']+'>'+sdata[i]['text']+'</div>').appendTo('.field.feedback-list');
				}
				$('.ui.modal.display').modal('show');
			}
		});
	});
}(window));