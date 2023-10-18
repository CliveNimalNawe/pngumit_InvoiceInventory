document.addEventListener('DOMContentLoaded', function() {
    var checkboxes = document.getElementsByClassName('item-checkbox');

    for (var i = 0; i < checkboxes.length; i++) {
      checkboxes[i].addEventListener('change', function() {
        var relatedDivId = this.getAttribute('id').replace('_checkbox', '_div');
        var relatedDiv = document.getElementById(relatedDivId);
        var relatedInputs = relatedDiv.getElementsByClassName('item-input');

        for (var j = 0; j < relatedInputs.length; j++) {
          relatedInputs[j].disabled = !this.checked;
        }
      });
    }
  });

  $(document).ready( function () {
  $('#myTable').DataTable();
  $('#dropdown').change(function() {
          var selectedId = $(this).val();
          
          $.ajax({
              type: 'POST',
              url: '/mission-entity-details',
              contentType: 'application/json',
              data: JSON.stringify({ id: selectedId }),
              success: function(response) {
                  document.getElementById('address').value=response.address;
              },
              error: function(error) {
                  console.log(error);
              }
          });
      });
    //Functions defined in here will execute when page loads. From inventory
    //Function to style flagged values when page loads
    function updateRows(){
        $('#myTable tbody tr').each(function() {
          var $row = $(this);
          var state = $row.find('.hidden-flag').data('state'); // Get the flag state
          // Assign flag colors based on the state
          if (state === 1) {
              $row.addClass('flagged-1');
          } else if (state === 2) {
              $row.addClass('flagged-2');
          }
          });
      }
  
      //Call on the defined function to update rows when page loads
      updateRows();
  
      //Event Listener to update rows if there is a change on detected on the table.
      table.on('draw.dt search.dt page.dt order.dt', function () {
          updateRows();
      });
        
      // Add a click event listener to toggle flags
      $('#myTable tbody').on('click', '.flag-button', function() {
        var button = $(this);
        var currentState = parseInt(button.data('state'), 10);
        var newState = (currentState + 1) % 3;
        var row = table.row(button.parents('tr'));
        
        //The test variables
        var rowData=row.data();
        $.ajax({
          url:'/update-flag',
          method: 'POST',
          data: JSON.stringify({ id: rowData[1], flag: newState }),
          contentType: 'application/json', // Set the content type to JSON
          dataType: 'json', // Expect JSON in the response
          success: function(response){
            if (response.success){
              // Update the button's text and data-state attribute
        button.data('state', newState);
        //updateButtonText(button, newState); //This has also been commneted out inline with the button case styling below
  
        // Update the hidden flag paragraph tag
        var hiddenFlag = row.node().getElementsByClassName('hidden-flag')[0];
        hiddenFlag.textContent = newState.toString();
  
  
        // Update the row's class based on the flag state
        row.node().classList.remove('flagged-0', 'flagged-1', 'flagged-2');
        row.node().classList.add('flagged-' + newState);
  
        // Update the database with the new state (you would need to implement this part)
        //updateDatabase(row.data(), newState);
              updateRows();
            }else{
              alert('Failed')
            }
          },
          error: function() {
            alert('failed')
          }
        });
  
      });
  
      // Initialize button text based on initial data-state attribute
      $('.flag-button').each(function() {
        var button = $(this);
        var initialState = parseInt(button.data('state'), 10);
        //updateButtonText(button, initialState); //This has also been commneted out inline with the button case styling below.
      });
  // Get the element with id="defaultOpen" and click on it
  document.getElementById("defaultOpen").click();
  } );
function openCity(evt, cityName) {
    // Declare all variables
    var i, tabcontent, tablinks;

    // Get all elements with class="tabcontent" and hide them
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    // Get all elements with class="tablinks" and remove the class "active"
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }

    // Show the current tab, and add an "active" class to the button that opened the tab
    document.getElementById(cityName).style.display = "block";
    evt.currentTarget.className += " active";
}
  /* This function may be used to change the buttons styling. Just commnented it out for future use.
  // Function to update the button text based on the flag state
  function updateButtonText(button, state) {
    switch (state) {
      case 0:
        button.text('Flag');
        break;
      case 1:
        button.text('Green');
        break;
      case 2:
        button.text('Red');
        break;
    }
    
  }
  */



