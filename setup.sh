echo "You have entered the Moderator setup script."
read -p "What is the access key (tip: NEVER SHOW THIS TO ANYONE OR ANY UN-TRUSTED PROGRAM)? > " access_key
read -p "What is the server ID of the server you would like to add this bot to? > " guild_id
read -p "What is the id of the log channel in your server (create one now if it doesn't exist)? >" log

echo -e "ARE YOU SURE THAT YOU WANT TO DO AS FOLLOWS:\n1. delete ./GUILD.json and ./ACCESS_KEY.txt if present\n2. write a new, generated .json file to ./GUILD.json\n3. write your inputted access key into ./ACCESS_KEY.txt"
read -p "Are you sure? (y/n, invalid answers = y) > " ans

if [[ $ans == "N" || $ans == "n" ]]; then
    exit 2 # abort
fi

cat <<EOF > ./GUILD.json
{
    "id": $guild_id,
    "LOG": $log
}
EOF

echo "$access_key" > ACCESS_KEY.txt