from bs4 import BeautifulSoup
import requests
import csv

# Download image from url
def download_image(url, filename):
    response = requests.get(url)

    if response.status_code == 200:
        # Save image to file
        with open(filename, 'wb') as file:
            file.write(response.content)
    else:
        print(f"Failed to download image. Status code: {response.status_code}")

def get_recipes():

    recipes_number = 0
    recipes = []

    # Iterate through pages of the website
    for i in range(2, 1500):
        # Get the page
        try:
            page_url = f"https://www.epicurious.com/recipes-menus?page={i}"
            response = requests.get(page_url)


            # If the status code is OK
            if response.status_code == 200:
                # create the soup
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Get the links in the page
                a_tags = soup.find_all('a', class_='SummaryItemHedLink-civMjp kHEkEM summary-item-tracking__hed-link summary-item__hed-link')
                
                # Get just the recipe link
                for a_tag in a_tags:
                    try:
                        relative_recipe_url = a_tag.get('href')
                        if "/food/views" in relative_recipe_url:
                            recipe_url = "https://www.epicurious.com" + relative_recipe_url

                            print(recipe_url)
                            recipes_number += 1
                            print(recipes_number)

                            # Get the recipe page
                            sub_response = requests.get(recipe_url)
                            if sub_response.status_code == 200:

                                sub_soup = BeautifulSoup(sub_response.text, "html.parser")

                                recipe_title = sub_soup.find("h1", class_="BaseWrap-sc-gjQpdd BaseText-ewhhUZ SplitScreenContentHeaderHed-lcUSuI iUEiRd hlsgKy dfelga").text

                                recipe_ingredients_html = sub_soup.find_all("div", class_="BaseWrap-sc-gjQpdd BaseText-ewhhUZ Description-cSrMCf iUEiRd ioVvSX fsKnGI")
                                recipe_ingredients = []
                                for ing in recipe_ingredients_html:
                                    recipe_ingredients.append(ing.text)
                                cleaned_ingredients = ','.join(recipe_ingredients)

                                recipe_instructions_html = sub_soup.find("li", class_="InstructionListWrapper-dcpygI kUNDwd").find_all("p")
                                recipe_instructions = ""
                                for inst in recipe_instructions_html:
                                    recipe_instructions += " " + inst.text
                                recipe_instructions = recipe_instructions.strip()

                                # Add the recipe to the recipes
                                recipes.append({
                                    "TranslatedRecipeName": recipe_title,
                                    "Cleaned-Ingredients": cleaned_ingredients,
                                    "TranslatedInstructions": recipe_instructions
                                })
                            else:
                                print(f"Error , cannot get the recipe page. Status Code: {response.status_code}")
                    except:
                        pass
            else:
                print(f"Error , cannot get the page {i}. Status Code: {response.status_code}")
        except:
            pass
    
    return recipes



# Save to csv file
def save_to_csv(recipes, csv_filename):
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['TranslatedRecipeName', 'Cleaned-Ingredients', 'TranslatedInstructions']
        csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        csv_writer.writeheader()
        csv_writer.writerows(recipes)

    print("csv file saves succesfully")

if __name__ == "__main__":
    recipes = get_recipes()
    save_to_csv(recipes, "recipes_3.csv")





