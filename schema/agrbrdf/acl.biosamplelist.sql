--
-- Name: biosamplelist; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE biosamplelist FROM PUBLIC;
REVOKE ALL ON TABLE biosamplelist FROM agrbrdf;
GRANT ALL ON TABLE biosamplelist TO agrbrdf;
GRANT SELECT ON TABLE biosamplelist TO gbs;


