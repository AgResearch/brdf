--
-- Name: biosampleob; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE biosampleob FROM PUBLIC;
REVOKE ALL ON TABLE biosampleob FROM agrbrdf;
GRANT ALL ON TABLE biosampleob TO agrbrdf;
GRANT SELECT ON TABLE biosampleob TO gbs;


