document.addEventListener("DOMContentLoaded", () => {
    let currentTeamIndex = 0;
    let settings = {};
    let teams = [];
    let draftedPlayers = {};

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
    const launchBtn = document.getElementById("launch-btn");
    const connectBtn = document.getElementById("connect-btn");
    const optimizeBtn = document.getElementById("optimize-btn");
    const teamSelect = document.getElementById("team-select");
    const browserSelect = document.getElementById("browser-select");
    const flashMessage = document.getElementById("flash-message");
    const tabLinks = document.querySelectorAll(".tab-link");

    connectBtn.addEventListener("click", connectToESPN);
    optimizeBtn.addEventListener("click", optimize);
    launchBtn.addEventListener("click", launchDriver);
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
            highlightPlayerIfSelected(tabContent);
        });
    });

    async function connectToESPN() {
        try {
            const response = await fetch('http://127.0.0.1:5000/scrape-ESPN2', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                })
            });
            
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const result = await response.json();
            teams = Object.keys(result);
            settings = result[teams[0]];
            //pickData = remove first team from result
            delete result[teams[0]];
            picksData = result;
            return initialize({ settings, picksData });
        } catch (error) {
            console.error('Error:', error);
        }
    }

    async function initialize({ settings, picksData }) {
        if (settings) {
            const teams = Object.keys(picksData);
            
            teamList.innerHTML = '';
            
            if (teamSelect.length == 0) {
                teamSelect.innerHTML = '';
            }

            teams.forEach((team, index) => {
                const teamItem = document.createElement("li");
                teamItem.textContent = team;
                if (index === currentTeamIndex) {
                    teamItem.classList.add("active");
                }
                teamList.appendChild(teamItem);

                const option = document.createElement("option");
                option.value = team;
                option.textContent = team;
                if (teamSelect.length < teams.length) {
                    teamSelect.appendChild(option);
                }
            });
            adjustCurrentPick(picksData);
            // Initialize an empty object to store the counts

            for (let team in picksData) {
                if (picksData.hasOwnProperty(team)) {
                    let playerList = picksData[team];
                    // Iterate over each player in the team
                    for (let playerIndex in playerList) {
                        if (playerList.hasOwnProperty(playerIndex)) {
                            let playerName = playerList[playerIndex];
                            let position = settings[playerIndex];
                            // Add position to player
                            picksData[team][playerIndex] = {
                                name: playerName,
                                position: position
                            };
                        }
                    }
                }
            }            

            let formattedTeams = {};

            for (let teamName in picksData) {
                if (picksData.hasOwnProperty(teamName)) {
                    let players = [];
                    for (let playerIndex in picksData[teamName]) {
                        if (picksData[teamName].hasOwnProperty(playerIndex)) {
                            let player = {
                                "Player": picksData[teamName][playerIndex].name,
                                "Pos": picksData[teamName][playerIndex].position
                            };
                            players.push(player);
                        }
                    }
                    formattedTeams[teamName] = players;
                }
            }

            let counts = {};
            // Loop through the keys of the json object
            for (let key in settings) {
                if (settings.hasOwnProperty(key)) {
                    let item = settings[key];
                    // If the item exists in counts, increment its count; otherwise, initialize it to 1
                    counts[item] = counts[item] ? counts[item] + 1 : 1;
                }
            }
            settings = Object.assign(settings, counts);
            draftedPlayers = formattedTeams;
            // need to add position to json for each player based on settings
            displayRosterRequirements(settings);
            const availablePlayers = await fetchAvailablePlayers();
            populatePlayers(availablePlayers);
        } else {
            console.error('Error: Could not find number of teams in API response');
        }
    }

    function highlightPlayerIfSelected(position) {
        const activePlayer = document.querySelector('#players-list li.active');
        if (activePlayer && activePlayer.textContent.includes(position)) {
            const playerName = activePlayer.textContent.split(' (')[0];
            highlightPlayer(playerName);
        }
    }

    async function launchDriver() {
        try {
            const response = await fetch('http://127.0.0.1:5000/launch-ESPN', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    browser: browserSelect.value,
                })
            });

            if (response.ok) {
                // response is string and not json
                const result = await response.text();
                console.log(result);
            } else {
                const errorResponse = await response.json();
                console.error('Error:', errorResponse);  // Handle the error response
                alert('Error launching ESPN: ' + errorResponse.error);
            }
        } catch (error) {
            console.error('Error:', error);
        }
    }

    async function fetchAvailablePlayers() {
        try {
            const playersData = await readCSVFiles();
            playersData.sort((a, b) => b.FPTS - a.FPTS);

            const availablePlayers = playersData.filter(player => {
                for (const teamPlayers of Object.values(draftedPlayers)) {
                    if (teamPlayers.some(draftedPlayer => draftedPlayer.Player.replace(/\./g, '') === player.Player)) {
                        return false;
                    }
                }
                return true;
            });

            return availablePlayers;
        } catch (error) {
            console.error('Error fetching available players:', error);
            return [];
        }
    }

    function populatePlayers(players) {
        Object.values(availablePlayersLists).forEach(list => list.innerHTML = '');

        players.forEach(player => {
            const playerItem = document.createElement("li");
            const teamText = player.Pos === 'DST' ? '' : ` - ${player.Team}`;
            playerItem.textContent = `${player.Player} (${player.Pos})${teamText}`;
            const vorp = document.createElement("span");
            vorp.classList = "vorp";
            vorp.textContent = `VORP: ${player.FPTS}`
            playerItem.appendChild(vorp);
            availablePlayersLists.overall.appendChild(playerItem);
            availablePlayersLists[player.Pos].appendChild(playerItem.cloneNode(true));
        });
    }

    function adjustCurrentPick(picksData) {
        let totalPlayers = 0;
        for (const team in picksData) {
            if (picksData.hasOwnProperty(team)) {
                let count = 0;
                for (const player of Object.values(picksData[team])) {
                    if (player.trim() !== "") { // Check if player name is not empty or whitespace
                        count++;
                    }
                }
                totalPlayers += count;
            }
        }
        const round = Math.floor(totalPlayers / teams.length);
        currentTeamIndex = totalPlayers % teams.length;
        const isAscending = (round % 2 === 0);
        currentTeamIndex = isAscending ? currentTeamIndex : teams.length - currentTeamIndex - 1;
        highlightCurrentTeam();   
    }

    function highlightCurrentTeam() {
        const teamItems = document.querySelectorAll("#team-list li");
        teamItems.forEach(item => item.classList.remove("active"));
        teamItems[currentTeamIndex].classList.add("active");
    }

    async function optimize() {
        try {
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
            highlightPlayer(result);
            const recommendedPlayer = document.querySelector(`#Recommendation`);
            recommendedPlayer.textContent = `Recommended Player: ${result}`;

            showFlashMessage("Done!", 'done');
        } catch (error) {
            console.error('Error:', error);
        }
    }

    function highlightPlayer(player) {
        const playerItems = document.querySelectorAll("#players-list li");
        playerItems.forEach(item => item.classList.remove("active"));
        playerItems.forEach(item => {
            if (item.textContent.includes(player)) {
                item.classList.add("active");
            }
        });
    }

    async function displayRosterRequirements(settings) {
        // make a dictionary from settings - i.e. how much each position shows up
        const rosterRequirements = document.createElement("div");
        rosterRequirements.classList.add("roster-requirements");

        // Helper function to create list items for each position
        function createPositionListItems(position, count, players = []) {
            let listItems = '';
            let playerIndex = 0;
            for (let i = 0; i < count; i++) {
                const player = players[playerIndex];
                if (player) {
                    listItems += `<li>${position}: ${player.Player} </li>`;
                    playerIndex++;
                } else {
                    listItems += `<li>${position}</li>`;
                }
            }
           
            return listItems;
        }
    
        // Get drafted players (assuming a global object draftedPlayers or a function to fetch them)
        // Example: const draftedPlayers = await getDraftedPlayers(draft_id);
    
        const selectedTeam = teamSelect.value; // Assume this is the team for which you want to display roster
        const teamDraftedPlayers = draftedPlayers[selectedTeam] || [];
    
        const positions = {
            'QB': settings.QB,
            'RB': settings.RB,
            'WR': settings.WR,
            'TE': settings.TE,
            'K': settings.K,
            'DST': settings.DST,
            'Flex': settings.FLEX,
            'Bench': settings.BE
        };
    
        rosterRequirements.innerHTML = `
            <h3></h3>
            <ul>
                ${createPositionListItems('QB', positions.QB, teamDraftedPlayers.filter(p => p.Pos === 'QB'))}
                ${createPositionListItems('RB', positions.RB, teamDraftedPlayers.filter(p => p.Pos === 'RB'))}
                ${createPositionListItems('WR', positions.WR, teamDraftedPlayers.filter(p => p.Pos === 'WR'))}
                ${createPositionListItems('TE', positions.TE, teamDraftedPlayers.filter(p => p.Pos === 'TE'))}
                ${createPositionListItems('Flex', positions.Flex, teamDraftedPlayers.filter(p => p.Pos === 'FLEX'))}
                ${createPositionListItems('K', positions.K, teamDraftedPlayers.filter(p => p.Pos === 'K'))}
                ${createPositionListItems('DST', positions.DST, teamDraftedPlayers.filter(p => p.Pos === 'DST'))}
                ${createPositionListItems('BE', positions.Bench, teamDraftedPlayers.filter(p => p.Pos === 'BE'))}
            </ul>
        `;
        document.getElementById("drafted-players").appendChild(rosterRequirements);
    }

    function showFlashMessage(message, type = 'connected') {
        flashMessage.textContent = message;
        flashMessage.style.display = 'inline-block';
        if (type === 'connected') {
            setTimeout(() => {
                flashMessage.style.display = 'none';
            }, 1000);
        }
        else if (type === 'optimizing') {
            setTimeout(() => {
                flashMessage.style.display = 'none';
            }, 10000);
        }
        else {
            setTimeout(() => {
                flashMessage.style.display = 'none';
            }, 1000);
        }
    }

    function teamSelectChange(){
        draftedPlayersList.innerHTML = "";
        console.log(settings);
        displayRosterRequirements(settings);
    }

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
