var canvas;
var ctx;

function init(){
	let width = $('.drawing-control button').width;
	$('.drawing-control button').css("height", width);
	$('#clear-button').on('click', function(evt){
		ctx.fillStyle="#fff";
		ctx.fillRect(0,0,canvas.width,canvas.height);
	});
	$('#try-button').on('click', function(evt){
		let img = canvas.toDataURL();
		let char = $("input[name='select-char']:checked").val();
		console.log("selected: " + char);
		sendImg(img, char);
		initModal();
	});

}

window.onload = function() {

	canvas = document.getElementById("drawing-canvas");
	ctx = canvas.getContext("2d");

	init();
    
    // Fill Window Width and Height
    canvas.width = 200;
	canvas.height = 200;
	
	// Set Background Color
    ctx.fillStyle="#fff";
    ctx.fillRect(0,0,canvas.width,canvas.height);
	
    // Mouse Event Handlers
	if(canvas){
		var isDown = false;
		var canvasX, canvasY;
		ctx.lineWidth = 5;
		
		$(canvas)
		.mousedown(function(e){
			isDown = true;
			ctx.beginPath();
            
            var br = document.getElementById("drawing-canvas").getBoundingClientRect();

			/*canvasX = e.pageX - canvas.offsetLeft;
			canvasY = e.pageY - canvas.offsetTop;*/
            
            canvasX = e.pageX - br.left;
			canvasY = e.pageY - br.top;

			ctx.moveTo(canvasX, canvasY);
		})
		.mousemove(function(e){
			if(isDown !== false) {

                var br = document.getElementById("drawing-canvas").getBoundingClientRect();

				/*canvasX = e.pageX - canvas.offsetLeft;
			canvasY = e.pageY - canvas.offsetTop;*/
            
            canvasX = e.pageX - br.left;
			canvasY = e.pageY - br.top;
				ctx.lineTo(canvasX, canvasY);
				ctx.strokeStyle = "#000";
				ctx.stroke();
			}
		})
		.mouseup(function(e){
			isDown = false;
			ctx.closePath();
		});
	}
	
	// Touch Events Handlers
	draw = {
		started: false,
		start: function(evt) {
            var br = document.getElementById("drawing-canvas").getBoundingClientRect();

			ctx.beginPath();
			ctx.moveTo(
				evt.touches[0].pageX - br.left,
				evt.touches[0].pageY - br.top
			);

			this.started = true;

		},
		move: function(evt) {
            var br = document.getElementById("drawing-canvas").getBoundingClientRect();

			if (this.started) {
				ctx.lineTo(
					evt.touches[0].pageX - br.left,
					evt.touches[0].pageY - br.top
				);

				ctx.strokeStyle = "#000";
				ctx.lineWidth = 3;
				ctx.stroke();
			}

		},
		end: function(evt) {
			this.started = false;
		}
	};
	
	// Touch Events
	canvas.addEventListener('touchstart', draw.start, false);
	canvas.addEventListener('touchend', draw.end, false);
	canvas.addEventListener('touchmove', draw.move, false);
	
	// Disable Page Move
	document.body.addEventListener('touchmove',function(evt){
		evt.preventDefault();
	},false);
};

function sendImg(img, char){
	let callback = (content, status) => {
		updateResult(JSON.parse(content));
	};

	$.post("/analyze?char=" + char,img, callback);
}

var obj;

function updateResult(result){

	obj = result;

	console.log(result, typeof(result));
	$("#result-loss").text(result.loss);
	$("#input-img").attr("src",result.input);
	$("#output-img").attr("src",result.output);
	$("#lossmap-img").attr("src",result.lossmap);
}


function initModal(){
		// create references to the modal...
	var modal = $('#myModal');
	// to all images -- note I'm using a class!
	var images = $('.modal');
	// the image in the modal
	var modalImg = $("#img01");

	// Go through all of the images with our custom class
	for (var i = 0; i < images.length; i++) {
	var img = images[i];
	// and attach our click listener for this image.
	img.addEventListener("click",function(evt) {
		console.log('modal img clicked');
		modal.css('display','block');
		modalImg.attr("src",this.src);
	});
	}

	var span = $(".close");

	span.click(function() {
		console.log('clicked');
		modal.css('display','none');
	});
}