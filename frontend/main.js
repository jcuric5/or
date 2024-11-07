const columnOrder = [
        "name",
        "location",
        "area",
        "purpose",
        "entrances",
        "nearest_bus_stop",
        "nearest_tram_stop",
        "nearest_train_stop",
        "nearest_parking"
];

function search() {
        const searchText = document.querySelector("#search-text").value;
        const searchField = document.querySelector("#search-field").value;

        const dbApiFetchSearch = `http://localhost:5555/search?text=${searchText}&field=${searchField}`

        fetch(dbApiFetchSearch).then(function(response) {
                return response.json();
        }).then(function(data) {
                const tableBody = document.querySelector("#datatable");

                tableBody.innerHTML = "";

                data.forEach(item => {
                        const row = document.createElement("tr");
                        
                        columnOrder.forEach(key => {
                                const cell = document.createElement("td");
                                cell.textContent = item[key];
                                cell.textContent = cell.textContent.replace(/,/g, ",\n");
                                row.appendChild(cell);
                        });
                
                        tableBody.appendChild(row);
                });

                // console.log(data);
        }).catch(function(err) {
                console.log(err);
        });
}

document.addEventListener("keydown", function(event) {
        if (event.key === "Enter") {
                search();
        }
});
