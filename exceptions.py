class UpdateRosterParameterWarning(Exception):
    def __str__(self):
        return "Warning: update_roster() should not be used without additional parameters, use get_roster() to access a roster without changing instead"
    
class AddPlayerToRosterParameterException(Exception):
    def __str__(self):
        return "Please provide some form of unique player specification, id_64, ozf_id, or player object"
    
