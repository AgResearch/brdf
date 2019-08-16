--
-- Name: geneticlocationlist; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE geneticlocationlist FROM PUBLIC;
REVOKE ALL ON TABLE geneticlocationlist FROM agrbrdf;
GRANT ALL ON TABLE geneticlocationlist TO agrbrdf;
GRANT SELECT ON TABLE geneticlocationlist TO gbs;


