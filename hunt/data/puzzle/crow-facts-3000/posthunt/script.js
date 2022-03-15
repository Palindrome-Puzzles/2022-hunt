var steps = [

    [['Thanks for signing up for Crow Facts 3000! You now will receive fun daily facts about CROWS! (*v*)', 'Crow Fact #11: Crow has a hut with some unusual legs, and there\'s something similar about his name.'],
     'To continue receiving Daily Crow Facts, reply \'crow\'',
     'crow'],

    [['Thanks for subscribing to Crow Facts!', 'Crow Fact #1: Crow is outstanding in his field and he\'s got being scary in the... well... you know...'],
     'Would you like to receive a Crow Fact every hour?\nReply \'J6w5346wd83hd3\' to continue',
     'j6w5346wd83hd3'],

    [['You now have a &lt;year&gt; subscription to Crow Facts and will receive fun &lt;hourly&gt; updates!', 'Crow Fact #9: If you saw Crow and then you saw a rhino, you might be experiencing deja vu.'],
     'To continue receiving Hourly Crow Facts, please estimate the number of turkeys that could fit in 26-100.',
     '5000'],

    [['You are subscribed to Crow Facts, your source for fascinating facts about crows!', 'Crow Fact #10: Crow has power over thunder and lightning, but before he uses it, he shouts \"I\'M CROW!\"'],
     'Prove you are human to continue by completing the following lyric: This can be the haziest \nThis can be the laziest \nThis can be the ___ Christmas of all.',
     'swayziest'],

    [['You will continue to receive Crow Facts every &lt;hour&gt;. Welcome to Crow Facts!', 'Crow Fact #21: Crow is the third in a line of ferocious monsters, all of which provide horrible sights to their captives.'],
     'To continue, please describe what you would give to be ambidexterous.',
     'righthand'],

    [['Thanks for texting Crow Facts! Remember, every time you text you will receive an instant Crow Fact!', 'Crow Fact #19: It takes one week for Crow to transform and rise out of the water.'],
     'To continue, reply with the name of the person who was really good in Mannequin.',
     'kimcattrall'],

    [['Thank you for subscribing to Crow Facts!', 'Crow Fact #15: Crow goes to great lengths to hide his very big feet.'],
     'To continue, who is your favorite robot?',
     'crowtrobot'],

    [['Crow Fact #14.07: Crow has everything. He has the face of a cat, the body of a snake, and the blade of an army knife.','Congrats! Here is your souvenir Crow map! <a href=\'https://bit.ly/crowfacts3000\' target=\'_blank\' rel=\'noopener nofollow noreferrer\'>https://bit.ly/crowfacts3000</a>'],
     'Please submit the answer to cancel Crow Facts.',
     'nowgoontotwitter'],

    [[],
     'Please do that instruction to cancel Crow Facts.',
'NOANSWER']

]

// Global vars
var step = -1;
var favorite = "crow";
var subscribed = true;

function send()
{
    // Respond to a message

    // Get message content
    var text_field = document.getElementById("text");
    message = text_field.value;

    if (message.length == 0) return;

    // Display the sent message
    add_bubble(message, "sent");

    // Calculate responses
    responses = get_responses(message);

    // Display responses
    for (i = 0; i < responses.length; ++i) {

	// Shorten responses to < 160 characters
	if (responses[i].length >= 160) {
	    responses[i] = responses[i].substring(0,156) + "...";
	}

	add_bubble(responses[i], "received");
    }

    // Clear the text field, set focus
    text_field.value = "";
    text_field.focus();
}

function add_bubble(message, type)
{
    // Add a <span> containing the message
    // type is "sent" or "received"

    var messages = document.getElementById("messages");
    messages.innerHTML += "<span class=\"" + type + "\">" + message + "</span>"
    messages.scrollTop = messages.scrollHeight;
}

function standardize_message(message)
{
    // Remove whitespace and make lowercase
    return message.replace(/\s/g,'').toLowerCase();
}

function get_responses(message)
{
    // Calculate the responses, based on the message

    responses = []

    if (standardize_message(message) == 'start' || standardize_message(message) == 'yes')
    {
	step = -1;
	subscribed = true;
    }

    if (!subscribed) {
	return [];
    }

    if (standardize_message(message) == 'stop' || standardize_message(message) == 'unsubscribe' || standardize_message(message) == 'cancel' || standardize_message(message) == 'quit')
    {
	subscribed = false;
	return ["You will not receive any more messages from this number. Reply START to try again."];
    }

    var correct = (step == -1 || standardize_message(message) == steps[step][2]);

    if (step == 2 && !isNaN(message) && standardize_message(message).length > 3) {
	       correct = true;
    }

    if (step == 6 && standardize_message(message) == "crowt.robot") {
	       correct = true;
    }


    if (correct) {
	++step;

	if (step > 8) step = 8;

	responses = responses.concat(steps[step][0]);

    }

    responses.push(steps[step][1]);

    return responses;
}
