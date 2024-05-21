document.addEventListener("DOMContentLoaded", () => {
    let currentTeamIndex = 0;
    const draftedPlayers = {};

    const teamList = document.getElementById("team-list");
    const availablePlayersList = document.getElementById("available-players");
    const draftedPlayersList = document.getElementById("drafted-players");
    const sleeperDraftIdInput = document.getElementById("sleeper-draft-id");
    const connectBtn = document.getElementById("connect-btn");
    const teamSelect = document.getElementById("team-select");
    const flashMessage = document.getElementById("flash-message");

    connectBtn.addEventListener("click", connectToSleeperDraft);

    teamSelect.addEventListener("change", teamSelectChange);

    function connectToSleeperDraft() {
        const draftId = sleeperDraftIdInput.value;
        if (draftId) {
            fetchSleeperDraftData(draftId);
            showFlashMessage("Successfully connected!");
        }
    }

    function teamSelectChange(){
        draftedPlayersList.innerHTML = "";
        // Update the drafted players list for the selected team
        const selectedTeam = teamSelect.value;
        if (draftedPlayers[selectedTeam]) {
            draftedPlayers[selectedTeam].forEach(player => {
                console.log(player)
                const draftedItem = document.createElement("li");
                draftedItem.textContent = `${player.Player} (${player.Pos}) - ${player.Team}`;
                draftedPlayersList.appendChild(draftedItem);
            });
        }
    }

    function showFlashMessage(message) {
        flashMessage.textContent = message;
        flashMessage.style.display = 'inline-block';

        setTimeout(() => {
            flashMessage.style.display = 'none';
        }, 1000);
    }

    async function fetchSleeperDraftData(draftId) {
        try {
            const picksResponse = await fetch(`https://api.sleeper.app/v1/draft/${draftId}/picks`);
            const picksData = await picksResponse.json();
            initialize(draftId, picksData);
        } catch (error) {
            console.error('Error fetching Sleeper draft data:', error);
        }
    }

    async function initialize(draftId, picksData) {
        try {
            const response = await fetch(`https://api.sleeper.app/v1/draft/${draftId}`);
            const data = await response.json();
            
            if (data && data.settings && data.settings.teams) {
                const numOfTeams = data.settings.teams;
                const teams = Array.from({ length: numOfTeams }, (_, index) => `Team ${index + 1}`);

                // Clear existing elements
                teamList.innerHTML = '';
                teamSelect.innerHTML = '';

                teams.forEach((team, index) => {
                    const teamItem = document.createElement("li");
                    teamItem.textContent = team;
                    if (index === currentTeamIndex) {
                        teamItem.classList.add("active");
                    }
                    teamList.appendChild(teamItem);
            
                    // Populate team dropdown
                    const option = document.createElement("option");
                    option.value = team;
                    option.textContent = team;
                    teamSelect.appendChild(option);
                });
                adjustCurrentPick(picksData.length, teams);
                updateDraftedPlayersList(picksData, teams);
                fetchAvailablePlayers(); // Fetch the available players
    
            } else {
                console.error('Error: Could not find number of teams in API response');
                return null;
            }
        } catch (error) {
            console.error('Error fetching number of teams:', error);
            return null;
        }
    }
    
    async function fetchAvailablePlayers() {
        try {
            // Read player data from CSV files
            const playersData = await readCSVFiles();
    
            // Sort players by FPTS
            playersData.sort((a, b) => b.FPTS - a.FPTS);
    
            // Filter out drafted players
            const availablePlayers = playersData.filter(player => {
                for (const teamPlayers of Object.values(draftedPlayers)) {
                    if (teamPlayers.some(draftedPlayer => draftedPlayer.Player === player.Player)) {
                        return false; // Player is drafted
                    }
                }
                return true; // Player is available
            });
    
            populatePlayers(availablePlayers);
        } catch (error) {
            console.error('Error fetching available players:', error);
        }
    }

    function populatePlayers(players) {
        availablePlayersList.innerHTML = ''; // Clear current list
    
        players.forEach(player => {
            const playerItem = document.createElement("li");
            const teamText = player.Pos === 'DST' ? '' : ` - ${player.Team}`;
            playerItem.textContent = `${player.Player} (${player.Pos})${teamText}`;
            availablePlayersList.appendChild(playerItem);
        });
    }    

    function updateDraftedPlayersList(data, teams) {
        // Clear the drafted players list
        draftedPlayersList.innerHTML = ""; // Clear current list
    
        // Populate drafted players
        let pickNumber = 1;
        let isAscending = true;
        
        data.forEach(pick => {
            // Calculate team name based on snaking order
            const teamName = `Team ${calculateTeamIndex(pickNumber, teams.length) + 1}`;
    
            if (!draftedPlayers[teamName]) {
                draftedPlayers[teamName] = [];
            }

            if (pick.pick_no<=teams.length) {
                draftedPlayers[teamName] = [];
            }
    
            draftedPlayers[teamName].push({
                Player: pick.metadata.first_name + " " + pick.metadata.last_name,
                Team: pick.metadata.team,
                Pos: pick.metadata.position
            });
    
            // Update pick number based on direction
            pickNumber += isAscending ? 1 : -1;
    
            // Toggle direction if necessary
            if (pickNumber < 1 || pickNumber > teams.length) {
                isAscending = !isAscending;
                pickNumber = isAscending ? 1 : teams.length;
            }
        });
    
        // Update the drafted players list for the selected team
        const selectedTeam = teamSelect.value;
        if (draftedPlayers[selectedTeam]) {
            draftedPlayers[selectedTeam].forEach(player => {
                console.log(player)
                const draftedItem = document.createElement("li");
                draftedItem.textContent = `${player.Player} (${player.Pos}) - ${player.Team}`;
                draftedPlayersList.appendChild(draftedItem);
            });
        }
    }    
    
    function adjustCurrentPick(draftedCount, teams) {
        const round = Math.floor(draftedCount / teams.length);
        currentTeamIndex = draftedCount % teams.length;
        isAscending = (round % 2 === 0);
        highlightCurrentTeam();
    }

    function highlightCurrentTeam() {
        const teamItems = document.querySelectorAll("#team-list li");
        teamItems.forEach(item => item.classList.remove("active"));
        teamItems[currentTeamIndex].classList.add("active");
    }

    function calculateTeamIndex(pickNumber, numberOfTeams) {
        // Calculate team index based on snaking order
        const roundNumber = Math.ceil(pickNumber / numberOfTeams);
        const withinRoundNumber = pickNumber % numberOfTeams;
        const isEvenRound = roundNumber % 2 === 0;
    
        if (isEvenRound) {
            return numberOfTeams - withinRoundNumber - 1;
        } else {
            return withinRoundNumber - 1;
        }
    }

    async function readCSVFiles() {
        // Array to store all player data from CSV files
        const allPlayersData = [];
    
        // Names of CSV files
        const csvFiles = ['FantasyPros_Fantasy_Football_Projections_K.csv', 'FantasyPros_Fantasy_Football_Projections_DST.csv', 'FantasyPros_Fantasy_Football_Projections_WR.csv', 'FantasyPros_Fantasy_Football_Projections_QB.csv', 'FantasyPros_Fantasy_Football_Projections_RB.csv', 'FantasyPros_Fantasy_Football_Projections_TE.csv'];
    
        // Read each CSV file and extract 'Player', 'Team', and 'FPTS' columns
        for (const csvFile of csvFiles) {
            const response = await fetch(csvFile);
            const text = await response.text();
            const csvData = Papa.parse(text, { header: true }).data;


            // Manually add the 'Pos' column based on the CSV file name
            const pos = csvFile.split('_').pop().split('.').shift().toUpperCase();
            csvData.forEach(player => player.Pos = pos);

            const filteredData = csvData.filter(player => player.Player.trim() !== '');

            // Extract and retain only the required columns
            const extractedData = filteredData.map(player => ({
                Player: player.Player,
                Team: player.Team,
                FPTS: player.FPTS,
                Pos: player.Pos
            }));
    
            allPlayersData.push(...extractedData);
        }

        return allPlayersData;
    }
});