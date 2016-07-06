(function(global){
	//if($('.suggestion-list').length) makePostRequest();
	//var interval = setInterval(makePostRequest,10000);
	var currentIdea;
	$(document).on('click','.proceed',function(e){
		$('.ui.modal.launchnext .teal.ui.label').html($(e.currentTarget.parentElement).siblings()[0].innerHTML);
		$('.ui.modal.launchnext').modal('show');
	});
	$(document).on('click','.startsuggestion',function(e){
		$('.ui.modal.launchnext').modal('hide');
		var feedbacks = $('input.feedback'), feedbackArray = [];
		for (var i = 0; i<feedbacks.length; i++){
			feedbackArray.push(feedbacks[i].value);
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
				$('tr.'+currentIdea+' td')[3].html('<div class="ui button view"><a href="#" class="ui label feedback-list count"><i class="icon doctor"></i>'+feedbacks.length+'</a></div>');
				console.log('launched suggestion seeking');
				$('.ui.modal.launchnext').modal('hide');
				$(e.currentTarget).prop('disabled',false);
				// makePostRequest();
			},
			error: function(e){
				console.log("error! "+e);
			}
		})
		
	});
	$(document).on('click','.cancelsuggestion',function(e){
		$('.ui.modal.launchnext').modal('hide');
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
		e.preventDefault();
		$.ajax({
			type: "GET",
			contentType: 'application/json; charset=utf-8',
			data: JSON.stringify({
				"idea_id":$(e.currentTarget.parentElement.parentElement).attr('class')
			}),
			url: '/get_feedbacks',
			success: function(sdata){
				sdata = sdata['feedbacks'];
				for (var i = 0; i < sdata.length; i++){
					$('<div class="feedback item "'+sdata['feedback_id']+'>'+sdata[text]+'</div>').appendTo('.field.feedback-list');
				}
			}
		})
	});
	

	// function makePostRequest(){
	// 	$.ajax({
	// 		type: "POST",
	// 		contentType: 'application/json; charset=utf-8',
	// 		data: JSON.stringify({
	// 			"problem_id": $('thead').attr('class')
	// 		}),
	// 		url: '/feedback_updates',
	// 		success:function(sdata){
	// 			sdata = sdata["ideas"]
	// 			for (var i= 0;i<sdata.length; i++){
	// 				if($('tr.'+sdata[i]['idea_id']+' .feedback-list').length)$('tr.'+sdata[i]['idea_id']+' .feedback-list')[0].innerHTML="<i class='doctor icon'></i> "+sdata[i]['feedback_count'];
	// 			}
	// 		}
	// 	})
	// }
}(window));