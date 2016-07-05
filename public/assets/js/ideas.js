(function(global){
	if($('.suggestion-list').length) makePostRequest();
    var interval = setInterval(makePostRequest,10000);
	var currentIdea;
	$(document).on('click','.proceed',function(e){
		$('.ui.modal .teal.ui.label').html($(e.currentTarget.parentElement).siblings()[0].innerHTML);
		$('.ui.modal').modal('show');
	});
	$(document).on('click','.startsuggestion',function(e){
		$('.ui.modal').modal('hide');
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
				$('tr.'+currentIdea+' td')[4].html('<div class="ui button view"><a href='+ sdata["suggestions_page_link"]+'><i class="icon doctor"></i>0</a></div>');
				console.log('launched suggestion seeking');
				$('.ui.modal').modal('hide');
				$(e.currentTarget).prop('disabled',false);
				makePostRequest();
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
	// $(document).on('click','.ui.button.view', function(e){
	// 	$('<div class="field"><input type="text" class="feedback" placeholder="Enter the feedback for the idea">').insertBefore($(e.currentTarget));
	// });
	

	function makePostRequest(){
		$.ajax({
			type: "POST",
			contentType: 'application/json; charset=utf-8',
			data: JSON.stringify({
				"problem_id": $('thead').attr('class')
			}),
			url: '/suggestion_updates',
			success:function(sdata){
			    sdata = sdata["ideas"]
				for (var i= 0;i<sdata.length; i++){
					if($('tr.'+sdata[i]['idea_id']+' .suggestion-list').length)$('tr.'+sdata[i]['idea_id']+' .suggestion-list')[0].innerHTML="<i class='doctor icon'></i> "+sdata[i]['suggestion_count'];
				}
			}
		})
	}
}(window));