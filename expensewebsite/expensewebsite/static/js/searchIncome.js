const searchField = document.querySelector("#searchField");
const tableOutput = document.querySelector(".table-output");
const appTable = document.querySelector(".app-table");
const paginationContainer = document.querySelector(".pagination-container");
const tableBody = document.querySelector(".table-body");

// Initially hide the table output
tableOutput.style.display = "none";

// Function to display a loading message
const showLoading = () => {
  tableBody.innerHTML = "<tr><td colspan='5' class='text-center'>Loading...</td></tr>";
};

// Function to handle search results display
const handleSearchResults = (data) => {
  if (data.length === 0) {
    tableBody.innerHTML = "<tr><td colspan='5' class='text-center'>No results found</td></tr>";
  } else {
    tableBody.innerHTML = data
      .map(
        (item) => `
          <tr>
            <td>${item.amount}</td>
            <td>${item.source}</td>
            <td>${item.description}</td>
            <td>${item.date}</td>
            <td>
              <a href="/income/income_edit/${item.id}" class="btn btn-secondary btn-sm">Edit</a>
            </td>
          </tr>`
      )
      .join("");
  }
};

// Function to handle errors
const handleError = (message) => {
  tableBody.innerHTML = `<tr><td colspan='5' class='text-center text-danger'>${message}</td></tr>`;
};

// Function to fetch search results
const fetchSearchResults = async (searchValue) => {
  showLoading();
  try {
    const response = await fetch("/income/search-income", {
      method: "POST",
      body: JSON.stringify({ searchText: searchValue }),
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error("Failed to fetch search results");
    }

    const data = await response.json();
    handleSearchResults(data);
  } catch (err) {
    console.error("Error:", err);
    handleError("Error fetching results. Please try again later.");
  }
};

// Function to handle search
const handleSearch = (searchValue) => {
  if (searchValue.trim().length > 0) {
    // Hide the default table and pagination
    paginationContainer.style.display = "none";
    appTable.style.display = "none";
    tableOutput.style.display = "block";

    // Fetch and display search results
    fetchSearchResults(searchValue);
  } else {
    // Reset to default table and pagination view when the search field is empty
    clearSearch();
  }
};

// Function to reset the table to default view
const clearSearch = () => {
  tableOutput.style.display = "none"; // Hide search results
  appTable.style.display = "block"; // Show the default table
  paginationContainer.style.display = "block"; // Show pagination
  tableBody.innerHTML = ""; // Clear search results table
};

// Event listener for the search field
searchField.addEventListener("keyup", (e) => {
  const searchValue = e.target.value;
  handleSearch(searchValue);
});

// Event listener for clearing search (optional, if needed)
document.querySelector("#clearSearchButton")?.addEventListener("click", clearSearch);
