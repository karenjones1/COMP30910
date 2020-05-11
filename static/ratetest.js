
//Function to return the user-inputted ratings
function saveRecommendations(element){
	console.log("click enter again RATE")
	const url = "localhost:4000/home"

	ratingVal = element.parentNode.getElementsByClassName("rating")[0].value;
	type = element.parentNode.parentNode.cells[2].innerHTML;

    console.log(element.parentNode.getElementsByClassName("rating")[0].value); //gets value of entered rating
    console.log(element.parentNode.parentNode.cells[2].innerHTML) // Gets the value in a cell e.g. hotel
    console.log(element.parentNode.parentNode.cells.length)

    var tableData = {"type":type, "rating":ratingVal};
    window.alert("Rating : "+ratingVal);
    
    fetch(`http://localhost:4000/ratings`, {
	    method: "POST",
	    body: JSON.stringify(tableData),
	    headers: {
            "Content-Type": "text/plain"
        },

  	})
}

