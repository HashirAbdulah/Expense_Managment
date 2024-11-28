const searchField = document.querySelector("#searchField");
const tableOutput = document.querySelector(".table-output");
const appTable = document.querySelector(".app-table");
const paginationContainer = document.querySelector(".pagination-container");
const tableBody = document.querySelector(".table-body");

// Initially hide the table output
tableOutput.style.display = "none";

// Function to handle search
const handleSearch = (searchValue) => {
  if (searchValue.trim().length > 0) {
    // Hide the default table and pagination
    paginationContainer.style.display = "none";
    appTable.style.display = "none";
    tableOutput.style.display = "block";

    // Clear previous search results
    tableBody.innerHTML = "";

    // Fetch search results from the server
    fetch("/expenses/search-expenses", {
      method: "POST",
      body: JSON.stringify({ searchText: searchValue }),
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((res) => {
        if (!res.ok) {
          throw new Error("Network response was not ok");
        }
        return res.json();
      })
      .then((data) => {
        console.log("Search results:", data);

        // Handle no results case
        if (data.length === 0) {
          tableOutput.innerHTML = "<p class='text-center'>No results found</p>";
        } else {
          // Populate the table with search results
          tableBody.innerHTML = data
            .map(
              (item) => `
                <tr>
                  <td>${item.amount}</td>
                  <td>${item.category}</td>
                  <td>${item.description}</td>
                  <td>${item.date}</td>
                  <td>
                    <a href="/expenses/expense_edit/${item.id}" class="btn btn-secondary btn-sm">Edit</a>
                  </td>
                </tr>`
            )
            .join("");
        }
      })
      .catch((err) => {
        console.error("Error fetching search results:", err);
        tableOutput.innerHTML = `<p class='text-center text-danger'>Error fetching results. Please try again later.</p>`;
      });
  } else {
    // Reset to default table and pagination view when the search field is empty
    tableOutput.style.display = "none";
    appTable.style.display = "block";
    paginationContainer.style.display = "block";
  }
};

// Function to handle clearing the search query
const clearSearch = () => {
  searchField.value = ""; // Clear the input field
  tableOutput.style.display = "none"; // Hide search results
  appTable.style.display = "block"; // Show the default table
  paginationContainer.style.display = "block"; // Show the pagination container
};

// Event listener for the search field
searchField.addEventListener("keyup", (e) => {
  const searchValue = e.target.value;
  handleSearch(searchValue);
});

