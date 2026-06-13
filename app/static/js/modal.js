document.addEventListener("click", function (event) {
	if (event.target.id === "close-modal") {
		document.body.dispatchEvent(
			new CustomEvent("modalClosed")
		);
	}
});

document.body.addEventListener("wishCreated", function () {
	document.getElementById("modal").innerHTML = "";
});

document.body.addEventListener("modalClosed", function () {
	document.getElementById("modal").innerHTML = "";
});
