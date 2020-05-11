
//Function which adds the selected checkboxes to an array
function checkboxtest(){
	console.log("click enter again")
	const url = "localhost:4000/home"

	var body = [];

	if(document.getElementById("CafeOrCoffeeShop").checked == true){
		body.push("CafeOrCoffeeShop");
	}
	if(document.getElementById("Restaurant").checked == true){
		body.push("Restaurant");
	}
	if(document.getElementById("PlaceOfWorship").checked == true){
		body.push("PlaceOfWorship");
	}
	if(document.getElementById("Museum").checked == true){
		body.push("Museum");
	}
	if(document.getElementById("ArtGallery").checked == true){
		body.push("ArtGallery");
	}
	if(document.getElementById("LandmarksOrHistoricalBuildings").checked == true){
		body.push("LandmarksOrHistoricalBuildings");
	}
	if(document.getElementById("Beach").checked == true){
		body.push("Beach");
	}
	if(document.getElementById("Landform").checked == true){
		body.push("Landform");
	}
	if(document.getElementById("Hotel").checked == true){
		body.push("Hotel");
	}
	if(document.getElementById("BedAndBreakfast").checked == true){
		body.push("BedAndBreakfast");
	}
	if(document.getElementById("Campground").checked == true){
		body.push("Campground");
	}
	if(document.getElementById("LodgingBusiness").checked == true){
		body.push("LodgingBusiness");
	}
	if(document.getElementById("GolfCourse").checked == true){
		body.push("GolfCourse");
	}
	if(document.getElementById("Park").checked == true){
		body.push("Park");
	}
	if(document.getElementById("SportsActivityLocation").checked == true){
		body.push("SportsActivityLocation");
	}
	if(document.getElementById("Stores").checked == true){
		body.push("Stores");
	}
	if(document.getElementById("BikeStore").checked == true){
		body.push("BikeStore");
	}
	if(document.getElementById("ShoppingCentre").checked == true){
		body.push("ShoppingCentre");
	}
	if(document.getElementById("LocalBusiness").checked == true){
		body.push("LocalBusiness");
	}





	fetch(`http://localhost:4000/testurl`, {
	    method: "POST",
	    body: JSON.stringify(body),
	    headers: {
            "Content-Type": "text/plain"
        },
  	}).then(()=> document.getElementById("formid").submit())

}


