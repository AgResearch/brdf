--
-- Name: staffob; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE staffob FROM PUBLIC;
REVOKE ALL ON TABLE staffob FROM agrbrdf;
GRANT ALL ON TABLE staffob TO agrbrdf;
GRANT SELECT ON TABLE staffob TO gbs;


