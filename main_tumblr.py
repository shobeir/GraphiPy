from tumblr_api import Tumblr
import pandas as pd


class USDE:
    def __init__(self, api):
        tumblr_api = api["tumblr"]
        self.tumblr = Tumblr(tumblr_api)

    def get_tumblr(self):
        return self.tumblr

    def exportCSV(self, dataframes, prefix):

        for key in dataframes.keys():
            dataframes[key].to_csv(
                prefix + "_" + key + ".csv", encoding="utf-8", index=False)

    def merge(self, main_df, target_df):

        for key in main_df.keys():
            main_df[key] = main_df[key].append(target_df[key])

    def remove_duplicates(self, df):

        for key in df.keys():
            if df[key].empty:
                continue
            if {"id"}.issubset(df[key].columns):
                df[key].drop_duplicates(subset=["id"], inplace=True)
            else:
                df[key].drop_duplicates(inplace=True)

    def get_df_from_list(self, df_list):

        temp_df = {}
        for key in df_list:
            temp_df[key] = None

        for key in temp_df.keys():
            temp_df[key] = pd.concat(df_list[key])

        return temp_df


def main():
    api = {
        "tumblr": {
            "consumer_key": ' ',
            "consumer_secret": ' ',
            "oauth_token": ' ',
            "oauth_secret": ' '
        }
    }

    usde = USDE(api)
    tumblr = usde.get_tumblr()

    df = tumblr.fetch_followed_blogs("lilized")
    df.export_all_CSV("tumblr_followed_blogs")

    df = tumblr.fetch_published_posts("overwatchbot")
    df.export_all_CSV("tumblr_published_posts")

    df = tumblr.fetch_liked_posts("lilized")
    df.export_all_CSV("tumblr_liked_posts")

    df = tumblr.fetch_posts_tagged(tag="overwatch")
    df.export_all_CSV("tumblr_posts_tagged")


if __name__ == '__main__':
    main()


