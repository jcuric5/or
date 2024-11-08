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

function jsonToCSV(json) {
        var array = typeof json != 'object' ? JSON.parse(json) : json;
        var str = "name,location,area,purpose,entrances,nearest_bus_stop,nearest_tram_stop,nearest_train_stop,nearest_parking\r\n";

        for (var i = 0; i < array.length; i++) {
                var line = '';

                for (var index in array[i]) {
                        if (line != "") line += ","

                        if (index == "purpose" || index == "entrances") {
                                line += "\"["
                        }

                        line += array[i][index];

                        if (index == "purpose" || index == "entrances") {
                                line += "]\""
                        }
                }

                str += line + '\r\n';
        }

        return str;
}

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

                document.getElementById("downloads").style.visibility = "visible";

                var dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(data));
                var jsonDownloadAnchorElem = document.getElementById("download-json");
                jsonDownloadAnchorElem.setAttribute("href", dataStr);
                jsonDownloadAnchorElem.setAttribute("download", "ZagrebPristupacnostParkova.json");

                var dataCsvStr = "data:text/csv;charset=utf-8," + encodeURIComponent(jsonToCSV(data));
                var csvDownloadAnchorElem = document.getElementById("download-csv");
                csvDownloadAnchorElem.setAttribute("href", dataCsvStr);
                csvDownloadAnchorElem.setAttribute("download", "ZagrebPristupacnostParkova.csv");
        }).catch(function(err) {
                console.log(err);
        });
}

document.addEventListener("keydown", function(event) {
        if (event.key === "Enter") {
                search();
        }
});
