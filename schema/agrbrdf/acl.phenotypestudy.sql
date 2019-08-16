--
-- Name: phenotypestudy; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE phenotypestudy FROM PUBLIC;
REVOKE ALL ON TABLE phenotypestudy FROM agrbrdf;
GRANT ALL ON TABLE phenotypestudy TO agrbrdf;
GRANT SELECT ON TABLE phenotypestudy TO gbs;


