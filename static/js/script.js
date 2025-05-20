document.addEventListener('DOMContentLoaded', function() {
  
  const selectedBets = [];
  
  initializeBettingUI();
  
  function initializeBettingUI() {
    
    const gameContainers = document.querySelectorAll('.mb-8.p-4.border.rounded-lg.shadow');
    
    gameContainers.forEach((container, index) => {
      const gameId = index + 1;
      
      const statusElement = container.querySelector('.mb-2.p-1.bg-gray-100.text-center.rounded span');
      const gameStatus = statusElement ? statusElement.textContent.trim() : '';
            
      const awayTeamElement = container.querySelector('.flex.flex-col.sm\\:grid.sm\\:grid-cols-12.sm\\:items-center.mb-2 .font-medium.text-base.sm\\:text-lg');
      const homeTeamElement = container.querySelector('.flex.flex-col.sm\\:grid.sm\\:grid-cols-12.sm\\:items-center.mt-2 .font-medium.text-base.sm\\:text-lg');
      
      const awayTeam = awayTeamElement ? awayTeamElement.textContent.trim() : '';
      const homeTeam = homeTeamElement ? homeTeamElement.textContent.trim() : '';     
      
      if (awayTeam && homeTeam) {
        
        const matchupElements = container.querySelectorAll('.truncate');
        matchupElements.forEach(element => {
          
          const isAwayRow = element.closest('.flex.flex-col.sm\\:grid.sm\\:grid-cols-12.sm\\:items-center.mb-2');
          const isHomeRow = element.closest('.flex.flex-col.sm\\:grid.sm\\:grid-cols-12.sm\\:items-center.mt-2');
          
          if (isAwayRow) {
            element.querySelector('.font-medium.text-base.sm\\:text-lg').textContent = awayTeam;
          } else if (isHomeRow) {
            element.querySelector('.font-medium.text-base.sm\\:text-lg').textContent = homeTeam;
          }
        });
      }
      
    
      const hasStarted = gameStatus.includes('P1') || 
                         gameStatus.includes('P2') || 
                         gameStatus.includes('P3') || 
                         gameStatus.includes('FINAL');
      
      if (!hasStarted) {
        
        setupGameButtons(container, gameId, awayTeam, homeTeam);
      } else {
      
        const buttons = container.querySelectorAll('button[type="button"]');
        buttons.forEach(button => {
          button.disabled = true;
          button.classList.add('opacity-50', 'cursor-not-allowed');
          button.classList.remove('hover:bg-blue-300');
        });
      }
    });
  }
  
  function setupGameButtons(container, gameId, awayTeam, homeTeam) {
    
    const buttons = container.querySelectorAll('button[type="button"]');
    
    buttons.forEach(button => {
      button.addEventListener('click', function() {
        
        const dataGroup = button.dataset.group || '';
        const dataValue = button.dataset.value || '';
        
        let betType = '';
        if (dataGroup.includes('moneyline')) {
          betType = 'moneyline';
        } else if (dataGroup.includes('total_over')) {
          betType = 'over';
        } else if (dataGroup.includes('total_under')) {
          betType = 'under';
        } else if (dataGroup.includes('spread')) {
          betType = 'spread';
        }
        
        const row = button.closest('.sm\\:grid.sm\\:grid-cols-12.sm\\:items-center');
        const teamNameElement = row ? row.querySelector('.font-medium.text-base.sm\\:text-lg') : null;
        const teamName = teamNameElement ? teamNameElement.textContent.trim() : `Game ${gameId}`;
            
        const matchup = `${awayTeam} @ ${homeTeam}`;
        
        let betDescription = '';
        let displayName = teamName;
             
        let odds = "-110";
                
        if (betType === 'spread') {
          
          const spreadOddsMatch = button.textContent.match(/\(([+-]\d+)\)/);
          if (spreadOddsMatch && spreadOddsMatch[1]) {
            odds = spreadOddsMatch[1];
          }
        } else if (betType === 'over' || betType === 'under') {
          
          const totalOddsMatch = button.textContent.match(/\(([+-]\d+)\)/);
          if (totalOddsMatch && totalOddsMatch[1]) {
            odds = totalOddsMatch[1];
          }
        } else if (betType === 'moneyline') {
        
          const moneylineOdds = button.textContent.trim().match(/([+-]\d+)/);
          if (moneylineOdds && moneylineOdds[1]) {
            odds = moneylineOdds[1];
          }
        }
        
        
        if (betType === 'over' || betType === 'under') {
          
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
          
          const spreadMatch = dataValue.match(/([+-]\d+\.?\d*)/);
          const spreadValue = spreadMatch ? spreadMatch[1] : '+1.5';
          
          betDescription = `${spreadValue}`;
          displayName = `${teamName} ${spreadValue}`;
        } else {
          betDescription = dataValue;
        }
        
        
        const isSelected = button.dataset.selected === "true";
        
        if (isSelected) {
          
          button.classList.remove('bg-green-500');
          button.classList.add('bg-blue-200');
          button.dataset.selected = "false";
          
          
          const betIndex = selectedBets.findIndex(bet => 
            bet.gameId === gameId && bet.betType === betType && bet.value === dataValue
          );
          
          if (betIndex !== -1) {
            selectedBets.splice(betIndex, 1);
          }
        } else {
          
          
          
          const groupPrefix = dataGroup.split('_')[0];
          
          
          if (betType === 'moneyline') {
            deselectButtonsByGroupPrefix(container, groupPrefix, 'spread');
          }
          
          
          if (betType === 'spread') {
            deselectButtonsByGroupPrefix(container, groupPrefix, 'moneyline');
            
            deselectButtonsByGroupPrefix(container, groupPrefix, 'spread');
          }
          
          
          if (betType === 'over') {
            deselectButtonsByGroupPrefix(container, groupPrefix, 'under');
          }
          
          
          if (betType === 'under') {
            deselectButtonsByGroupPrefix(container, groupPrefix, 'over');
          }
          
          
          const sameGroupButtons = container.querySelectorAll(`[data-group="${dataGroup}"]`);
          sameGroupButtons.forEach(btn => {
            if (btn !== button) {
              btn.classList.remove('bg-green-500');
              btn.classList.add('bg-blue-200');
              btn.dataset.selected = "false";
              
              
              const btnValue = btn.dataset.value;
              const betIndex = selectedBets.findIndex(bet => 
                bet.gameId === gameId && bet.betType === betType && bet.value === btnValue
              );
              
              if (betIndex !== -1) {
                selectedBets.splice(betIndex, 1);
              }
            }
          });
          
          
          button.classList.remove('bg-blue-200');
          button.classList.add('bg-green-500');
          button.dataset.selected = "true";
          
          
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
        
        
        updateRightPanel();
      });
    });
  }
  
  
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

  
  function deselectButtonsByGroupPrefix(container, groupPrefix, typeToDeselect) {
    const buttons = container.querySelectorAll('button[type="button"]');
    
    buttons.forEach(button => {
      const group = button.dataset.group || '';
    
      if (group.startsWith(groupPrefix) && group.includes(typeToDeselect)) {
        if (button.dataset.selected === "true") {
          button.classList.remove('bg-green-500');
          button.classList.add('bg-blue-200');
          button.dataset.selected = "false";
          
          
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
  
  
  function updateRightPanel() {
    const selectionsContainer = document.getElementById('selections-container');
    
    if (!selectionsContainer) return;
    
    if (selectedBets.length === 0) {
      selectionsContainer.innerHTML = '<p class="text-sm text-gray-400">Make selections from the games to see them here</p>';
      return;
    }
    
    
    let html = `
      <div class="flex items-center mb-4">
        <div class="bg-blue-500 text-white rounded-full w-6 h-6 flex items-center justify-center mr-2">
          ${selectedBets.length}
        </div>
        <h2 class="text-xl font-bold text-white">Betslip</h2>
      </div>
    `;
    
    
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
      
      
      <div id="success-message" class="mt-3 p-3 bg-green-700 text-white rounded-lg hidden">
        Bet successfully placed! Your bet information has been recorded.
      </div>
      
      
      <div id="error-message" class="mt-3 p-3 bg-red-700 text-white rounded-lg hidden">
        There was an error placing your bet. Please try again.
      </div>
    `;
    
    selectionsContainer.innerHTML = html;
    
    
    const betAmountInput = document.getElementById('bet-amount');
    if (betAmountInput) {
      betAmountInput.addEventListener('input', calculatePotentialWinnings);
      calculatePotentialWinnings(); 
    }
    
    
    const placeBetButton = document.getElementById('place-bet-button');
    if (placeBetButton) {
      placeBetButton.addEventListener('click', submitBetToGoogleSheet);
    }
  }
  
  
  function calculateParlayOdds(bets) {
    let decimalOdds = 1;
    
    bets.forEach(bet => {
      
      const americanOdds = parseInt(bet.odds) || -110; 
      let decimal;
      
      if (americanOdds > 0) {
        decimal = (americanOdds / 100) + 1;
      } else {
        decimal = (100 / Math.abs(americanOdds)) + 1;
      }
      
      decimalOdds *= decimal;
    });
    
    
    let americanOdds;
    if (decimalOdds >= 2) {
      americanOdds = Math.round((decimalOdds - 1) * 100);
    } else {
      americanOdds = Math.round(-100 / (decimalOdds - 1));
    }
    
    return americanOdds.toString();
  }
  
  
  function calculatePotentialWinnings() {
    if (selectedBets.length === 0) return;
    
    const betAmountInput = document.getElementById('bet-amount');
    const potentialWinningsElement = document.getElementById('potential-winnings');
    
    if (!betAmountInput || !potentialWinningsElement) return;
    
    const betAmount = parseFloat(betAmountInput.value) || 0;
    let winnings = 0;
    
    try {
      if (selectedBets.length === 1) {
        
        const bet = selectedBets[0];
        const americanOdds = parseInt(bet.odds) || -110;
        
        if (americanOdds > 0) {
          winnings = betAmount * (americanOdds / 100);
        } else {
          winnings = betAmount * (100 / Math.abs(americanOdds));
        }
      } else if (selectedBets.length > 1) {
        
        const parlayOdds = calculateParlayOdds(selectedBets);
        const americanOdds = parseInt(parlayOdds) || -110;
        
        if (americanOdds > 0) {
          winnings = betAmount * (americanOdds / 100);
        } else {
          winnings = betAmount * (100 / Math.abs(americanOdds));
        }
      }

      
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

  
  function formatOdds(odds) {
    try {
      const numOdds = parseInt(odds);
      if (isNaN(numOdds) || !isFinite(numOdds)) {
        return "-110";
      }
      return numOdds > 0 ? `+${numOdds}` : numOdds.toString();
    } catch (error) {
      return "-110";
    }
  }

  
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
    
    const scriptURL = 'https://script.google.com/macros/s/AKfycbx3NjdIw6A907c582_RXZSsZdhS4tIJKTqDNkbNBFGlmgV3Nc5J3VHZdPJeYds-B1fa/exec';

    fetch(scriptURL, {
      method: 'POST',
      body: JSON.stringify(formData),
      headers: {
        'Content-Type': 'application/json'
      }
    })
    .then(response => {
      console.log('Success:', response);
      
      if (placeBetButton) {
        placeBetButton.disabled = false;
        placeBetButton.textContent = 'Place Bet';
        placeBetButton.classList.remove('opacity-75');
      }
      
      document.getElementById('success-message').classList.remove('hidden');
    })
    .catch(error => {
      console.error('Error:', error);
      
      if (placeBetButton) {
        placeBetButton.disabled = false;
        placeBetButton.textContent = 'Place Bet';
        placeBetButton.classList.remove('opacity-75');
      }
    
      document.getElementById('error-message').classList.remove('hidden');
    });
  }
});
