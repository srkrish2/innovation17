(function(global){
	$('.rateit.button').popup({
		hoverable: true,
		position: 'bottom left',
		delay: {
			show: 300,
			hide: 800
		}
	});
	$('.ui.rating')
	.rating({
		maxRating: 5,
		clearable: true
	});
	$(document).on('click', '.rate.submit', function(e){
		$(e.currentTarget).prop('disabled',true);
		$.ajax({
			type: "POST",
			url: "/post_rating",
			contentType: 'application/json; charset=utf-8',
			data: JSON.stringify({
				'id': $(e.currentTarget).parents('.item.inspiration').attr('class').split(' ')[2],
				'type':'inspiration',
				'novelty': $(e.currentTarget).siblings('table').find('.ui.rating.novel').rating('get rating'),
				'usefulness': $(e.currentTarget).siblings('table').find('.ui.rating.usefulness').rating('get rating')
			}),
			success: function(sdata){
				console.log('submmited ratingof inspiration');
				$(e.currentTarget).prop('disabled',false);
			},
			error: function(e){
				console.log("error! "+e);
				$(e.currentTarget).prop('disabled',false);
			}
		});
	})
	$(document).on('click','.proceed',function(e){
		$('.ui.modal').modal('show');
	});
	$(document).on('click','.startidea',function(e){
		$(e.currentTarget).prop('disabled',true);
		$('.ui.modal').hide();
		$.ajax({
			type: 'POST',
			url: '/post_idea_task',
			contentType: 'application/json; charset=utf-8',
			data: JSON.stringify({
				'problem_id':$('.divided').attr('class').split(' ')[4],//length of class list is 4
				'count_goal': $('.count_goal').val()
			}),
			success: function(sdata){
				console.log('launched idea');
				window.location.replace('/'+sdata['url']);
				$(e.currentTarget).prop('disabled',false);
			},
			error: function(e){
				console.log("error! "+e);
				$(e.currentTarget).prop('disabled',false);
			}
		})	
	});

	$(document).on('click','.cancelidea',function(e){
		$('.ui.modal').modal('hide');
	});
	$(document).on('click','.rj-all, .ac-all',function(e){
		
		$.ajax({
			type: "POST",
			url: '/batch_rj',
			data: JSON.stringify({
				"to_reject": $(e.currentTarget).hasClass('ac-all'),
				"type": itemType,
				"parent_id":$('.ui.divided.items').attr('class').split(' ')[3]
			}),
			success: function(sdata){
				if($(e.currentTarget).hasClass('ac-all'))
				{
					$('.ui.buttons :not(.hidden) > .ui.button.ac').addClass('active');
					$('.ui.buttons :not(.hidden) > .ui.button.rj').removeClass('active');
				}
				else {
					$('.ui.buttons :not(.hidden) > .ui.button.rj').addClass('active');
					$('.ui.buttons :not(.hidden) > .ui.button.ac').removeClass('active');
				}
			}
		})
		
	});
	$(document).on('click','.rj, .ac, .reactivate',function(e){
		var itemType = "inspiration", toreject=$(e.currentTarget).hasClass('red'), item_id = $(e.currentTarget.parentElement.parentElement.parentElement).attr('class').split(' ')[2];//the fourth class name
		$(e.currentTarget).prop('disabled',true);
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
				$(e.currentTarget).prop('disabled',false);
				if($(e.currentTarget).hasClass('reactivate')){
					$(e.currentTarget).html('Activated into accepted');
				}
				else {
					if(toreject){
						$(e.currentTarget).addClass('active');
						$(e.currentTarget).siblings().removeClass('active');
						// $(e.currentTarget).html('Accept');
					}
					else {
						$(e.currentTarget).addClass('active');
						$(e.currentTarget).siblings().removeClass('active');
					}
				}
				console.log('rejected schema id '+item_id);
			},
			error: function(e){
				console.log('error! ' + e);
			}
		});
	});
	
	$(function(){
		$('.ui.accordion').accordion()
	});
}(window));