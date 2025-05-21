document.addEventListener('DOMContentLoaded', function() {
  // Store selected bets and their odds
  const selectedBets = [];
  
  // Initialize the UI
  initializeBettingUI();
  
  /**
   * Initialize the betting UI and set up event listeners
   */
  function initializeBettingUI() {
    // Find all game containers (each game is in a div with class "mb-8 p-4 border rounded-lg shadow")
    const gameContainers = document.querySelectorAll('.mb-8.p-4.border.rounded-lg.shadow');
    
    gameContainers.forEach((container, index) => {
      const gameId = index + 1; // Use the index+1 as game ID
      
      // Find the game status element (div with class "mb-2 p-1 bg-gray-100 text-center rounded")
      const statusElement = container.querySelector('.mb-2.p-1.bg-gray-100.text-center.rounded span');
      const gameStatus = statusElement ? statusElement.textContent.trim() : '';
      
      // Check if the game has started or finished (P1, P2, P3, FINAL)
      const hasStarted = gameStatus.includes('P1') || 
                         gameStatus.includes('P2') || 
                         gameStatus.includes('P3') || 
                         gameStatus.includes('FINAL');
      
      if (!hasStarted) {
        // Game has not started yet, enable buttons
        setupGameButtons(container, gameId);
      } else {
        // Game has started or finished, disable buttons
        const buttons = container.querySelectorAll('button[type="button"]');
        buttons.forEach(button => {
          button.disabled = true;
          button.classList.add('opacity-50', 'cursor-not-allowed');
          button.classList.remove('hover:bg-blue-300');
        });
      }
    });
  }
  
  /**
   * Set up event listeners for buttons in games that have started
   */
  function setupGameButtons(container, gameId) {
    // 1. grab all the buttons in this game
    const buttons = container.querySelectorAll('button[type="button"]');
  
    // 2. grab your two team‐row divs
    const teamRows = container.querySelectorAll('.team-row');
    let awayTeam = '', homeTeam = '';
  
    if (teamRows.length >= 2) {
      awayTeam = teamRows[0]
        .querySelector('.font-medium')
        .textContent.trim();
      homeTeam = teamRows[1]
        .querySelector('.font-medium')
        .textContent.trim();
    }
  
    // 3. wire up each button
    buttons.forEach(button => {
      button.addEventListener('click', function() {
        const dataGroup = button.dataset.group || '';
        const dataValue = button.dataset.value || '';
    
        // 1) Determine betType exactly as you already do:
        let betType = '';
        if (dataGroup.includes('_moneyline'))       betType = 'moneyline';
        else if (dataGroup.includes('_total_over'))  betType = 'over';
        else if (dataGroup.includes('_total_under')) betType = 'under';
        else if (dataGroup.includes('_spread_'))     betType = 'spread';
    
        // 2) Grab the row THIS button lives in:
        const thisRow = button.closest('.team-row');
    
        // 3) If it's moneyline or spread, the teamName is whatever that row says:
        let teamName;
        if (betType === 'moneyline' || betType === 'spread') {
          teamName = thisRow
            .querySelector('.font-medium')
            .textContent
            .trim();
        }
        // 4) If it's over/under, you might want a “Total X” label instead:
        else if (betType === 'over' || betType === 'under') {
          const parts = dataValue.split(' ');
          teamName = `${betType === 'over' ? 'Over' : 'Under'} ${parts[1]}`; 
        }
        // 5) Otherwise fallback to Game#
        else {
          teamName = `Game ${gameId}`;
        }
    
        // 6) Full away @ home for the mini-line below
        const matchup = `${awayTeam} @ ${homeTeam}`;
  
        // Extract specific bet details
        let betDescription = '';
        let displayName = teamName;
        
        // Get the actual odds directly from the button text
        let odds = "-110"; // Default odds
        
        // Extract odds from button text - fix for spread odds
        if (betType === 'spread') {
          // For spread bets, find the odds portion in parentheses
          const spreadOddsMatch = button.textContent.match(/\(([+-]\d+)\)/);
          if (spreadOddsMatch && spreadOddsMatch[1]) {
            odds = spreadOddsMatch[1];
          }
        } else if (betType === 'over' || betType === 'under') {
          // For total over/under, find the odds portion in parentheses
          const totalOddsMatch = button.textContent.match(/\(([+-]\d+)\)/);
          if (totalOddsMatch && totalOddsMatch[1]) {
            odds = totalOddsMatch[1];
          }
        } else if (betType === 'moneyline') {
          // For moneyline, the odds are usually the main text
          const moneylineOdds = button.textContent.trim().match(/([+-]\d+)/);
          if (moneylineOdds && moneylineOdds[1]) {
            odds = moneylineOdds[1];
          }
        }
        
        // Process bet details based on type
        if (betType === 'over' || betType === 'under') {
          // Extract the total value (e.g., "O 5.5" or "U 5.5")
          const totalMatch = dataValue.match(/[OU]\s*(\d+\.?\d*)/);
          const totalValue = totalMatch ? totalMatch[1] : '5.5';
          
          if (betType === 'over') {
            betDescription = `Over ${totalValue}`;
            displayName = `Over ${totalValue}`;
          } else {
            betDescription = `Under ${totalValue}`;
            displayName = `Under ${totalValue}`;
          }
        } else if (betType === 'spread') {
          // Extract the spread value (e.g., "+1.5" or "-1.5")
          const spreadMatch = dataValue.match(/([+-]\d+\.?\d*)/);
          const spreadValue = spreadMatch ? spreadMatch[1] : '+1.5';
          
          betDescription = `${spreadValue}`;
          displayName = `${teamName} ${spreadValue}`;
        } else {
          betDescription = dataValue;
        }
        
        // Check if button is already selected
        const isSelected = button.dataset.selected === "true";
        
        if (isSelected) {
          // Deselect this button
          button.classList.remove('bg-green-500');
          button.classList.add('bg-blue-200');
          button.dataset.selected = "false";
          
          // Remove this bet from selectedBets
          const betIndex = selectedBets.findIndex(bet => 
            bet.gameId === gameId && bet.betType === betType && bet.value === dataValue
          );
          
          if (betIndex !== -1) {
            selectedBets.splice(betIndex, 1);
          }
        } else {
          // Handle mutual exclusivity rules
          
          // Get all buttons in this game with the same group prefix
          const groupPrefix = dataGroup.split('_')[0]; // e.g., "game1" from "game1_moneyline"
          
          // If selecting a moneyline, deselect any spread for this game
          if (betType === 'moneyline') {
            deselectButtonsByGroupPrefix(container, groupPrefix, 'spread');
          }
          
          // If selecting a spread, deselect any moneyline for this game
          if (betType === 'spread') {
            deselectButtonsByGroupPrefix(container, groupPrefix, 'moneyline');
            // Also deselect any other spread buttons for this game
            deselectButtonsByGroupPrefix(container, groupPrefix, 'spread');
          }
          
          // If selecting over, deselect any under for this game
          if (betType === 'over') {
            deselectButtonsByGroupPrefix(container, groupPrefix, 'under');
          }
          
          // If selecting under, deselect any over for this game
          if (betType === 'under') {
            deselectButtonsByGroupPrefix(container, groupPrefix, 'over');
          }
          
          // Deselect other buttons in the same group
          const sameGroupButtons = container.querySelectorAll(`[data-group="${dataGroup}"]`);
          sameGroupButtons.forEach(btn => {
            if (btn !== button) {
              btn.classList.remove('bg-green-500');
              btn.classList.add('bg-blue-200');
              btn.dataset.selected = "false";
              
              // Remove from selectedBets if it was selected
              const btnValue = btn.dataset.value;
              const betIndex = selectedBets.findIndex(bet => 
                bet.gameId === gameId && bet.betType === betType && bet.value === btnValue
              );
              
              if (betIndex !== -1) {
                selectedBets.splice(betIndex, 1);
              }
            }
          });
          
          // Select this button
          button.classList.remove('bg-blue-200');
          button.classList.add('bg-green-500');
          button.dataset.selected = "true";
          
          // Add this bet to selectedBets
          selectedBets.push({
            gameId,
            betType,
            value: dataValue,
            description: betDescription,
            displayName: displayName,
            team: teamName,
            matchup: matchup,
            awayTeam: awayTeam,
            homeTeam: homeTeam,
            odds: odds,
            betTypeLabel: getBetTypeLabel(betType)
          });
        }
        
        // Update the right panel
        updateRightPanel();
      });
    });
  }
  
  /**
   * Get a readable label for the bet type
   */
  function getBetTypeLabel(betType) {
    switch(betType) {
      case 'moneyline':
        return 'MONEYLINE';
      case 'over':
      case 'under':
        return 'TOTAL';
      case 'spread':
        return 'SPREAD';
      default:
        return betType.toUpperCase();
    }
  }
  
  /**
   * Deselect buttons by group prefix and type
   */
  function deselectButtonsByGroupPrefix(container, groupPrefix, typeToDeselect) {
    const buttons = container.querySelectorAll('button[type="button"]');
    
    buttons.forEach(button => {
      const group = button.dataset.group || '';
      
      // Check if this button belongs to the group prefix and contains the type to deselect
      if (group.startsWith(groupPrefix) && group.includes(typeToDeselect)) {
        if (button.dataset.selected === "true") {
          button.classList.remove('bg-green-500');
          button.classList.add('bg-blue-200');
          button.dataset.selected = "false";
          
          // Get the bet type based on the group
          let betType = '';
          if (group.includes('moneyline')) {
            betType = 'moneyline';
          } else if (group.includes('total_over')) {
            betType = 'over';
          } else if (group.includes('total_under')) {
            betType = 'under';
          } else if (group.includes('spread')) {
            betType = 'spread';
          }
          
          // Remove from selectedBets
          const dataValue = button.dataset.value;
          const betIndex = selectedBets.findIndex(bet => 
            bet.gameId === parseInt(groupPrefix.replace('game', '')) && 
            bet.betType === betType && 
            bet.value === dataValue
          );
          
          if (betIndex !== -1) {
            selectedBets.splice(betIndex, 1);
          }
        }
      }
    });
  }
  
  /**
   * Update the right panel with selected bets - FanDuel style with left alignment
   */
  function updateRightPanel() {
    const selectionsContainer = document.getElementById('selections-container');
    
    if (!selectionsContainer) return;
    
    if (selectedBets.length === 0) {
      selectionsContainer.innerHTML = '<p class="text-sm text-gray-400">Make selections from the games to see them here</p>';
      return;
    }
    
    // Create the betslip header
    let html = `
      <div class="flex items-center mb-4">
        <div class="bg-blue-500 text-white rounded-full w-6 h-6 flex items-center justify-center mr-2">
          ${selectedBets.length}
        </div>
        <h2 class="text-xl font-bold text-white">Betslip</h2>
      </div>
    `;
    
    // Add each selected bet in FanDuel style with left alignment
    selectedBets.forEach(bet => {
      const oddsText = formatOdds(bet.odds);
      
      html += `
        <div class="mb-3 bg-gray-800 rounded-lg overflow-hidden">
          <div class="p-3">
            <div class="flex justify-between items-start">
              <div class="flex-1 text-left">
                <div class="text-lg font-semibold text-white">${bet.displayName}</div>
                <div class="text-sm text-gray-400 uppercase">${bet.betTypeLabel}</div>
                <div class="text-xs text-gray-500 mt-1">${bet.awayTeam} @ ${bet.homeTeam}</div>
              </div>
              <div class="text-right">
                <div class="text-lg font-bold text-white">${oddsText}</div>
                <button class="text-xs bg-gray-700 text-white px-2 py-1 rounded mt-1">CASH OUT</button>
              </div>
            </div>
          </div>
        </div>
      `;
    });
    
    // Add parlay odds if there are multiple bets
    if (selectedBets.length > 1) {
      const parlayOdds = calculateParlayOdds(selectedBets);
      html += `
        <div class="mb-3 bg-gray-700 rounded-lg p-3">
          <div class="flex justify-between items-center">
            <div class="text-white font-medium">${selectedBets.length} leg parlay</div>
            <div class="text-white font-bold">${formatOdds(parlayOdds)}</div>
          </div>
        </div>
      `;
    }
    
    // Add bet amount input and potential winnings in FanDuel style - side by side
    html += `
      <div class="mt-4 grid grid-cols-2 gap-3">
        <div class="bg-gray-800 rounded-lg p-3">
          <div class="text-sm text-gray-400 mb-1">WAGER</div>
          <div class="flex items-center">
            <span class="text-white text-lg mr-1">$</span>
            <input type="number" id="bet-amount" class="w-full bg-transparent text-white text-lg border-none p-0 focus:outline-none" value="10" min="1">
          </div>
        </div>
        
        <div class="bg-gray-800 rounded-lg p-3">
          <div class="text-sm text-gray-400 mb-1">TO WIN</div>
          <div id="potential-winnings" class="text-green-400 font-bold text-lg">$0.00</div>
        </div>
      </div>
      
      <button id="place-bet-button" class="mt-4 w-full bg-green-600 hover:bg-green-700 text-white font-bold py-3 rounded-lg">
        Place Bet
      </button>
      
      <!-- Success message (hidden by default) -->
      <div id="success-message" class="mt-3 p-3 bg-green-700 text-white rounded-lg hidden">
        Bet successfully placed! Your bet information has been recorded.
      </div>
      
      <!-- Error message (hidden by default) -->
      <div id="error-message" class="mt-3 p-3 bg-red-700 text-white rounded-lg hidden">
        There was an error placing your bet. Please try again.
      </div>
    `;
    
    selectionsContainer.innerHTML = html;
    
    // Re-attach event listener to the new bet amount input
    const betAmountInput = document.getElementById('bet-amount');
    if (betAmountInput) {
      betAmountInput.addEventListener('input', calculatePotentialWinnings);
      calculatePotentialWinnings(); // Calculate initial winnings
    }
    
    // Attach event listener to the place bet button
    const placeBetButton = document.getElementById('place-bet-button');
    if (placeBetButton) {
      placeBetButton.addEventListener('click', submitBetToGoogleSheet);
    }
  }
  
  /**
   * Calculate parlay odds for multiple bets
   */
  function calculateParlayOdds(bets) {
    let decimalOdds = 1;
    
    bets.forEach(bet => {
      // Make sure we have valid odds
      const americanOdds = parseInt(bet.odds) || -110; // Default to -110 if parsing fails
      let decimal;
      
      if (americanOdds > 0) {
        decimal = (americanOdds / 100) + 1;
      } else {
        decimal = (100 / Math.abs(americanOdds)) + 1;
      }
      
      decimalOdds *= decimal;
    });
    
    // Convert back to American odds
    let americanOdds;
    if (decimalOdds >= 2) {
      americanOdds = Math.round((decimalOdds - 1) * 100);
    } else {
      americanOdds = Math.round(-100 / (decimalOdds - 1));
    }
    
    return americanOdds.toString();
  }
  
  /**
   * Calculate potential winnings based on bet amount and selected bets
   */
  function calculatePotentialWinnings() {
    if (selectedBets.length === 0) return;
    
    const betAmountInput = document.getElementById('bet-amount');
    const potentialWinningsElement = document.getElementById('potential-winnings');
    
    if (!betAmountInput || !potentialWinningsElement) return;
    
    const betAmount = parseFloat(betAmountInput.value) || 0;
    let winnings = 0;
    
    try {
      if (selectedBets.length === 1) {
        // Single bet
        const bet = selectedBets[0];
        const americanOdds = parseInt(bet.odds) || -110; // Default to -110 if parsing fails
        
        if (americanOdds > 0) {
          winnings = betAmount * (americanOdds / 100);
        } else {
          winnings = betAmount * (100 / Math.abs(americanOdds));
        }
      } else if (selectedBets.length > 1) {
        // Parlay bet
        const parlayOdds = calculateParlayOdds(selectedBets);
        const americanOdds = parseInt(parlayOdds) || -110; // Default to -110 if parsing fails
        
        if (americanOdds > 0) {
          winnings = betAmount * (americanOdds / 100);
        } else {
          winnings = betAmount * (100 / Math.abs(americanOdds));
        }
      }
      
      // Check for invalid results
      if (isNaN(winnings) || !isFinite(winnings)) {
        potentialWinningsElement.textContent = "$0.00";
      } else {
        potentialWinningsElement.textContent = `$${winnings.toFixed(2)}`;
      }
    } catch (error) {
      console.error("Error calculating winnings:", error);
      potentialWinningsElement.textContent = "$0.00";
    }
  }
  
  /**
   * Format odds for display
   */
  function formatOdds(odds) {
    try {
      const numOdds = parseInt(odds);
      if (isNaN(numOdds) || !isFinite(numOdds)) {
        return "-110"; // Default value if parsing fails
      }
      return numOdds > 0 ? `+${numOdds}` : numOdds.toString();
    } catch (error) {
      return "-110"; // Default value if any error occurs
    }
  }
  
  /**
   * Submit bet information to Google Sheets
   */
  function submitBetToGoogleSheet() {
    if (selectedBets.length === 0) {
      alert("Please select at least one bet before submitting");
      return;
    }
  
    const betAmountInput = document.getElementById('bet-amount');
    const potentialWinningsElement = document.getElementById('potential-winnings');
  
    if (!betAmountInput || !potentialWinningsElement) return;
  
    const betAmount = parseFloat(betAmountInput.value) || 0;
    const potentialWinnings = potentialWinningsElement.textContent.replace('$', '');
  
    const betType = selectedBets.length > 1 ? 'Parlay' : 'Single';
  
    let odds;
    if (selectedBets.length === 1) {
      odds = formatOdds(selectedBets[0].odds);
    } else {
      odds = formatOdds(calculateParlayOdds(selectedBets));
    }
  
    const betDetails = selectedBets.map(bet => {
      return {
        matchup: `${bet.awayTeam} @ ${bet.homeTeam}`,
        team: bet.team,
        betType: bet.betTypeLabel,
        selection: bet.displayName,
        odds: formatOdds(bet.odds)
      };
    });
  
    const formData = {
      date: new Date().toISOString(),
      betType: betType,
      numberOfLegs: selectedBets.length,
      wagerAmount: betAmount.toFixed(2),
      potentialWinnings: potentialWinnings,
      totalOdds: odds,
      betDetails: JSON.stringify(betDetails)
    };
  
    const placeBetButton = document.getElementById('place-bet-button');
    if (placeBetButton) {
      placeBetButton.disabled = true;
      placeBetButton.textContent = 'Placing Bet...';
      placeBetButton.classList.add('opacity-75');
    }
  
    document.getElementById('success-message').classList.add('hidden');
    document.getElementById('error-message').classList.add('hidden');
  
    const scriptURL = 'https://script.google.com/macros/s/AKfycbyMtVtJoxsGVAFxOMsS2jYkS9gaoBI_sGe0q8rOMeU0yFsi5TU-HitaxZxtN-70KpGqww/exec';
    
    fetch(scriptURL, {
      method: 'POST',
      mode: 'no-cors', // 👈 Needed to bypass CORS restrictions
      body: JSON.stringify(formData)
    })
    .then(() => {
      if (placeBetButton) {
        placeBetButton.disabled = false;
        placeBetButton.textContent = 'Place Bet';
        placeBetButton.classList.remove('opacity-75');
      }
      document.getElementById('success-message').classList.remove('hidden');
    })
    .catch(() => {
      if (placeBetButton) {
        placeBetButton.disabled = false;
        placeBetButton.textContent = 'Place Bet';
        placeBetButton.classList.remove('opacity-75');
      }
      document.getElementById('error-message').classList.remove('hidden');
    });
  }
});
