document.addEventListener("DOMContentLoaded", () => {
    let currentTeamIndex = 0;
    const draftedPlayers = {};

    const teamList = document.getElementById("team-list");
    const availablePlayersLists = {
        overall: document.getElementById("available-players-overall"),
        QB: document.getElementById("available-players-QB"),
        RB: document.getElementById("available-players-RB"),
        WR: document.getElementById("available-players-WR"),
        TE: document.getElementById("available-players-TE"),
        K: document.getElementById("available-players-K"),
        DST: document.getElementById("available-players-DST"),
    };
    const draftedPlayersList = document.getElementById("drafted-players");
    const sleeperDraftIdInput = document.getElementById("sleeper-draft-id");
    const connectBtn = document.getElementById("connect-btn");
    const optimizeBtn = document.getElementById("optimize-btn");
    const teamSelect = document.getElementById("team-select");
    const flashMessageConnected = document.getElementById("flash-message-connected");
    const flashMessageOptimizing = document.getElementById("flash-message-optimizing");
    const tabLinks = document.querySelectorAll(".tab-link");

    connectBtn.addEventListener("click", connectToSleeperDraft);
    optimizeBtn.addEventListener("click", optimize);

    teamSelect.addEventListener("change", teamSelectChange);

    
    tabLinks.forEach(tab => {
        tab.addEventListener("click", () => {
            tabLinks.forEach(link => link.classList.remove("active"));
            tab.classList.add("active");
            const tabContent = tab.dataset.tab;
            document.querySelectorAll(".tab-content").forEach(content => {
                content.classList.remove("active");
            });
            availablePlayersLists[tabContent].classList.add("active");
            // Highlight player if their position matches the active tab
            highlightPlayerIfSelected(tabContent);
        });
    });

    function highlightPlayerIfSelected(position) {
        const activePlayer = document.querySelector('#players-list li.active');
        
        // If an active player is found, reapply the highlight
        if (activePlayer && activePlayer.textContent.includes(position)) {
            const playerName = activePlayer.textContent.split(' (')[0]; // Extract player name
            highlightPlayer(playerName);
        }
    }


    function connectToSleeperDraft() {
        const draftId = sleeperDraftIdInput.value;
        if (draftId) {
            fetchSleeperDraftData(draftId);
            showFlashMessage("Successfully connected!");
        }
    }

    async function optimize() {
        try {            
            // Send the data to the Python server
            showFlashMessage("Optimizing...", 'optimizing');
            const response = await fetch('http://127.0.0.1:5000/process-info', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    draft_id: sleeperDraftIdInput.value
                })
            });
    
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
    
            const result = await response.json();
            console.log('Result from Python:', result);
            highlightPlayer(result);
            showFlashMessage("Complete", 'complete');
            
        } catch (error) {
            console.error('Error:', error);
        }
    }    

    function highlightPlayer(player) {
        // Find the player in current tab and set it as active
        const playerItems = document.querySelectorAll("#players-list li");
        playerItems.forEach(item => item.classList.remove("active"));
        playerItems.forEach(item => {
            if (item.textContent.includes(player)) {
                item.classList.add("active");
            }
        });        
    }
    

    function teamSelectChange(){
        draftedPlayersList.innerHTML = "";
        // Update the drafted players list for the selected team
        const selectedTeam = teamSelect.value;
        if (draftedPlayers[selectedTeam]) {
            draftedPlayers[selectedTeam].forEach(player => {
                const draftedItem = document.createElement("li");
                draftedItem.textContent = `${player.Player} (${player.Pos}) - ${player.Team}`;
                draftedPlayersList.appendChild(draftedItem);
            });
        }
    }

    function showFlashMessage(message, type = 'connected') {
        if (type === 'connected') {
            flashMessageConnected.textContent = message;
            flashMessageConnected.style.display = 'inline-block';

            setTimeout(() => {
                flashMessageConnected.style.display = 'none';
            }, 1000);
        }
        else if (type === 'optimizing') {
            flashMessageOptimizing.textContent = message;
            flashMessageOptimizing.style.display = 'inline-block';

            setTimeout(() => {
                flashMessageOptimizing.style.display = 'none';
            }, 10000);
        }
        else {
            flashMessageOptimizing.textContent = message;
            flashMessageOptimizing.style.display = 'inline-block';

            setTimeout(() => {
                flashMessageOptimizing.style.display = 'none';
            }, 1000);
        }
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
                if(data.league_id){
                    getLeagueSettings(data.league_id);
                } else {
                    settings = getLeagueSettingsNoLeague(draftId);
                }

    
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
                    if (teamPlayers.some(draftedPlayer => draftedPlayer.Player.replace(/\./g, '') === player.Player)) {
                        return false; // Player is drafted
                    }
                }
                return true; // Player is available
            });
    
            populatePlayers(availablePlayers);
            return availablePlayers;
        } catch (error) {
            console.error('Error fetching available players:', error);
            return [];
        }
    }

    function populatePlayers(players) {
        Object.values(availablePlayersLists).forEach(list => list.innerHTML = ''); // Clear current lists
    
        players.forEach(player => {
            const playerItem = document.createElement("li");
            const teamText = player.Pos === 'DST' ? '' : ` - ${player.Team}`;
            playerItem.textContent = `${player.Player} (${player.Pos})${teamText}`;
    
            availablePlayersLists.overall.appendChild(playerItem); // Add to overall list
            availablePlayersLists[player.Pos].appendChild(playerItem.cloneNode(true)); // Add to position-specific list
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

    async function getLeagueSettingsNoLeague(draft_id) {
        try {
            const response = await fetch(`https://api.sleeper.app/v1/draft/${draft_id}`);
            const data = await response.json();
            const keys = Object.keys(data.settings);
            const QBs = data.settings[keys[4]];
            const RBs = data.settings[keys[3]];
            const WRs = data.settings[keys[1]];
            const TEs = data.settings[keys[2]];
            const Ks = data.settings[keys[5]];
            const DSTs = data.settings[keys[7]];
            const flex = data.settings[keys[6]];
            //const scoring = data.metadata[keys[0]];
            var settings = {
                QBs: QBs,
                RBs: RBs,
                WRs: WRs,
                TEs: TEs,
                Ks: Ks,
                DSTs: DSTs,
                flex: flex,
                //scoring: scoring
            }
            return settings;
        } catch (error) {
            console.error('Error fetching settings:', error);
            return null;
        }
    }

    // write function that takes in draft id, and gets league_id
    // async function getLeagueSettings(league_id) {
    //     try {
    //         const response = await fetch(`GET https://api.sleeper.app/v1/${league_id}`);
    //         const data = await response.json();
    //         console.log(data.scoring_settings);
    //         console.log(data.roster_positions);
    //     } catch (error) {
    //         console.error('Error fetching league ID:', error);
    //         return null;
    //     }
    // }

    async function readCSVFiles() {
        // Array to store all player data from CSV files
        const allPlayersData = [];
    
        // Names of CSV files
        // const csvFiles = ['FantasyPros_Fantasy_Football_Projections_K.csv', 'FantasyPros_Fantasy_Football_Projections_DST.csv', 'FantasyPros_Fantasy_Football_Projections_WR.csv', 'FantasyPros_Fantasy_Football_Projections_QB.csv', 'FantasyPros_Fantasy_Football_Projections_RB.csv', 'FantasyPros_Fantasy_Football_Projections_TE.csv'];
        const csvFile = ['../vorp2024.csv']
        // Read each CSV file and extract 'Player', 'Team', and 'FPTS' columns
        const response = await fetch(csvFile);
        const text = await response.text();
        const csvData = Papa.parse(text, { header: true }).data;

        const filteredData = csvData.filter(player => player.Player.trim() !== '');

        // Extract and retain only the required columns
        const extractedData = filteredData.map(player => ({
            Player: player.Player.replace(/\./g, ''),
            Team: player.Team,
            FPTS: player.VORP,
            Pos: player.POS
        }));

        allPlayersData.push(...extractedData);
        

        return allPlayersData;
    }
});